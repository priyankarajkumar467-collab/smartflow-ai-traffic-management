"""
SMARTFLOW AI - VEHICLE DETECTION & TRAFFIC ANALYSIS

YOLOv8 + ByteTrack
Case Study: Oppanakara Street, Coimbatore
"""

import cv2
import json
from pathlib import Path
from collections import defaultdict, Counter

from ultralytics import YOLO

from ai.traffic_logic import (
    LOW,
    MEDIUM,
    HIGH,
    calculate_density,
    calculate_queue_length,
    calculate_green_time,
    determine_signal_action
)


# ============================================================
# PROJECT PATHS AND CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

VIDEO_PATH = BASE_DIR / "data" / "traffic_video.mp4"
MODEL_PATH = BASE_DIR / "yolov8n.pt"
OUTPUT_PATH = BASE_DIR / "results" / "analysis_results.json"

CASE_STUDY = "Oppanakara Street, Coimbatore"


# ============================================================
# VEHICLE CLASSES
# ============================================================

VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck"
}


# ============================================================
# SIGNAL DECISION REASON
# ============================================================

def create_signal_reason(density, queue_length, green_time):

    if density == HIGH:
        return (
            f"High traffic with {queue_length} estimated queued "
            f"vehicles. Green time is extended to "
            f"{green_time} seconds."
        )

    elif density == MEDIUM:
        return (
            f"Medium traffic with {queue_length} estimated queued "
            f"vehicles. Normal green timing is recommended."
        )

    else:
        return (
            f"Low traffic with {queue_length} estimated queued "
            f"vehicles. Green time can be reduced to "
            f"{green_time} seconds."
        )


# ============================================================
# MAIN FUNCTION
# ============================================================

def main():

    print("=" * 65)
    print("SMARTFLOW AI - TRAFFIC ANALYSIS")
    print("YOLOv8 + ByteTrack")
    print("=" * 65)

    # --------------------------------------------------------
    # CHECK VIDEO FILE
    # --------------------------------------------------------

    if not VIDEO_PATH.is_file():
        print(f"ERROR: Video not found: {VIDEO_PATH}")
        return

    # --------------------------------------------------------
    # LOAD YOLO MODEL
    # --------------------------------------------------------

    print("\nLoading YOLOv8 model...")

    try:
        model = YOLO(str(MODEL_PATH))
        print("YOLOv8 model loaded successfully.")

    except Exception as error:
        print(f"ERROR: Could not load YOLO model: {error}")
        return

    # --------------------------------------------------------
    # READ VIDEO INFORMATION
    # --------------------------------------------------------

    video = cv2.VideoCapture(str(VIDEO_PATH))

    if not video.isOpened():
        print("ERROR: Could not open traffic video.")
        video.release()
        return

    try:
        fps = video.get(cv2.CAP_PROP_FPS)

        total_frames = int(
            video.get(cv2.CAP_PROP_FRAME_COUNT)
        )

    finally:
        video.release()

    if fps <= 0:
        fps = 30.0

    video_duration = total_frames / fps

    print(f"\nVideo FPS       : {fps:.2f}")
    print(f"Total Frames    : {total_frames}")
    print(f"Video Duration  : {video_duration:.2f} seconds")

    # --------------------------------------------------------
    # INITIALIZE TRACKING DATA
    # --------------------------------------------------------

    vehicle_class_history = defaultdict(list)

    queue_ids = set()

    frames_processed = 0

    # --------------------------------------------------------
    # YOLO + BYTETRACK PROCESSING
    # --------------------------------------------------------

    print("\nStarting YOLOv8 + ByteTrack analysis...")
    print("-" * 65)

    try:

        results = model.track(
            source=str(VIDEO_PATH),
            tracker="bytetrack.yaml",
            conf=0.4,
            stream=True,
            verbose=False
        )

        for result in results:

            frames_processed += 1

            if result.orig_shape:
                frame_height = result.orig_shape[0]
            else:
                continue

            if result.boxes is None:
                continue

            if result.boxes.id is None:
                continue

            track_ids = result.boxes.id.cpu().tolist()

            class_ids = result.boxes.cls.cpu().tolist()

            boxes = result.boxes.xyxy.cpu().tolist()

            # ------------------------------------------------
            # PROCESS DETECTIONS
            # ------------------------------------------------

            for track_id, class_id, box in zip(
                track_ids,
                class_ids,
                boxes
            ):

                track_id = int(track_id)
                class_id = int(class_id)

                if class_id not in VEHICLE_CLASSES:
                    continue

                vehicle_type = VEHICLE_CLASSES[class_id]

                # Store vehicle class history
                vehicle_class_history[track_id].append(
                    vehicle_type
                )

                # --------------------------------------------
                # QUEUE ESTIMATION
                # --------------------------------------------

                x1, y1, x2, y2 = box

                center_y = (y1 + y2) / 2

                queue_threshold = frame_height * 0.60

                if center_y > queue_threshold:
                    queue_ids.add(track_id)

            # ------------------------------------------------
            # DISPLAY PROCESSING PROGRESS
            # ------------------------------------------------

            if frames_processed % 100 == 0:

                print(
                    f"Processed frames: "
                    f"{frames_processed}/{total_frames}"
                )

    except Exception as error:

        print(f"\nERROR during vehicle detection: {error}")
        return

    # ========================================================
    # FINAL VEHICLE CLASSIFICATION
    # ========================================================

    final_vehicle_types = {}

    for track_id, class_history in vehicle_class_history.items():

        if not class_history:
            continue

        most_common_class = Counter(
            class_history
        ).most_common(1)[0][0]

        final_vehicle_types[track_id] = most_common_class

    # ========================================================
    # COUNT UNIQUE VEHICLES
    # ========================================================

    vehicle_counts = {
        "car": 0,
        "motorcycle": 0,
        "bus": 0,
        "truck": 0
    }

    for vehicle_type in final_vehicle_types.values():

        if vehicle_type in vehicle_counts:
            vehicle_counts[vehicle_type] += 1

    unique_vehicles = len(final_vehicle_types)

    # --------------------------------------------------------
    # NORMAL AND HEAVY VEHICLES
    # --------------------------------------------------------

    normal_vehicles = (
        vehicle_counts["car"]
        + vehicle_counts["motorcycle"]
    )

    heavy_vehicles = (
        vehicle_counts["bus"]
        + vehicle_counts["truck"]
    )

    classification_total = (
        normal_vehicles + heavy_vehicles
    )

    if classification_total != unique_vehicles:

        print("\nWARNING:")
        print(
            "Vehicle classification total does not match "
            "unique vehicle total."
        )

    # --------------------------------------------------------
    # HEAVY VEHICLE PERCENTAGE
    # --------------------------------------------------------

    if unique_vehicles > 0:

        heavy_percentage = (
            heavy_vehicles / unique_vehicles
        ) * 100

    else:
        heavy_percentage = 0

    heavy_percentage = round(heavy_percentage, 2)

    # ========================================================
    # QUEUE CALCULATION
    # ========================================================

    estimated_queue = calculate_queue_length(queue_ids)

    estimated_queue = min(
        estimated_queue,
        unique_vehicles
    )

    # ========================================================
    # TRAFFIC DENSITY
    # ========================================================

    density, queue_ratio = calculate_density(
        estimated_queue,
        unique_vehicles
    )

    # ========================================================
    # ADAPTIVE GREEN TIME
    # ========================================================

    green_time = calculate_green_time(
        estimated_queue,
        density
    )

    # ========================================================
    # SIGNAL DECISION
    # ========================================================

    decision = determine_signal_action(density)

    reason = create_signal_reason(
        density,
        estimated_queue,
        green_time
    )

    # ========================================================
    # CREATE JSON OUTPUT
    # ========================================================

    analysis_data = {

        "project": {

            "name": "SmartFlow",

            "title":
                "AI-Based Adaptive Traffic Signal Management",

            "case_study":
                CASE_STUDY
        },

        "analysis": {

            "video_fps":
                round(fps, 2),

            "total_frames":
                total_frames,

            "video_duration_seconds":
                round(video_duration, 2),

            "frames_processed":
                frames_processed,

            "unique_vehicles":
                unique_vehicles,

            "estimated_queue":
                estimated_queue,

            "queue_ratio_percent":
                queue_ratio,

            "traffic_density":
                density
        },

        "vehicle_classification": {

            "car":
                vehicle_counts["car"],

            "motorcycle":
                vehicle_counts["motorcycle"],

            "bus":
                vehicle_counts["bus"],

            "truck":
                vehicle_counts["truck"],

            "normal_vehicles":
                normal_vehicles,

            "heavy_vehicles":
                heavy_vehicles,

            "heavy_vehicle_percentage":
                heavy_percentage
        },

        "adaptive_signal": {

            "recommended_green_time_seconds":
                green_time,

            "signal_decision":
                decision,

            "decision_reason":
                reason
        },

        "ai_pipeline": {

            "vehicle_detection":
                "YOLOv8",

            "multi_object_tracking":
                "ByteTrack",

            "vehicle_counting":
                "Completed",

            "vehicle_classification":
                "Completed",

            "queue_estimation":
                "Completed",

            "traffic_density":
                "Completed",

            "adaptive_green_time":
                "Completed",

            "signal_decision":
                "Completed"
        },

        "vehicle_categories": {

            "normal": [
                "car",
                "motorcycle"
            ],

            "heavy": [
                "bus",
                "truck"
            ]
        },

        "validation_note":
            "Traffic improvement metrics are prototype estimates "
            "and are not field-measured results."
    }

    # ========================================================
    # SAVE JSON FILE
    # ========================================================

    try:

        OUTPUT_PATH.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            OUTPUT_PATH,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                analysis_data,
                file,
                indent=4
            )

    except (OSError, TypeError, ValueError) as error:

        print(f"ERROR: Could not save analysis results: {error}")
        return

    # ========================================================
    # FINAL OUTPUT
    # ========================================================

    print("\n")
    print("=" * 65)
    print("SMARTFLOW AI ANALYSIS COMPLETED")
    print("=" * 65)

    print(f"\nFrames Processed      : {frames_processed}")
    print(f"Unique Vehicles       : {unique_vehicles}")

    print("\nVEHICLE CLASSIFICATION")
    print("-" * 40)

    print(f"Cars                  : {vehicle_counts['car']}")
    print(f"Motorcycles           : {vehicle_counts['motorcycle']}")
    print(f"Buses                 : {vehicle_counts['bus']}")
    print(f"Trucks                : {vehicle_counts['truck']}")

    print("\nVEHICLE CATEGORY")
    print("-" * 40)

    print(f"Normal Vehicles       : {normal_vehicles}")
    print(f"Heavy Vehicles        : {heavy_vehicles}")
    print(f"Heavy Vehicle %       : {heavy_percentage}%")

    print("\nTRAFFIC ANALYSIS")
    print("-" * 40)

    print(f"Estimated Queue       : {estimated_queue}")
    print(f"Queue Ratio           : {queue_ratio}%")
    print(f"Traffic Density       : {density}")

    print("\nADAPTIVE SIGNAL")
    print("-" * 40)

    print(f"Recommended Green     : {green_time} seconds")
    print(f"Signal Decision       : {decision}")

    print("\nDecision Reason:")
    print(reason)

    print("\nResults saved to:")
    print(OUTPUT_PATH)

    print("\n" + "=" * 65)


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()