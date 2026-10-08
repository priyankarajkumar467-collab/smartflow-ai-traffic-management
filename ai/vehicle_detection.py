from ultralytics import YOLO
import cv2
import json
import os


# ============================================================
# SMARTFLOW - AI TRAFFIC ANALYSIS
# YOLOv8 + ByteTrack + Adaptive Signal Management
# Case Study: Oppanakara Street, Coimbatore
# ============================================================

VIDEO_PATH = "data/traffic_video.mp4"
MODEL_PATH = "yolov8n.pt"


print("\n========================================")
print("SMARTFLOW AI TRAFFIC ANALYSIS")
print("========================================")


# ------------------------------------------------------------
# 1. LOAD MODEL
# ------------------------------------------------------------

print("\nLoading YOLOv8 model...")

model = YOLO(MODEL_PATH)

print("YOLOv8 model loaded successfully.")


# ------------------------------------------------------------
# 2. VIDEO INFORMATION
# ------------------------------------------------------------

video = cv2.VideoCapture(VIDEO_PATH)

if not video.isOpened():
    print("ERROR: Could not open traffic video.")
    exit()

fps = video.get(cv2.CAP_PROP_FPS)
frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)

video.release()

duration_seconds = frame_count / fps

print("\n--- VIDEO INFORMATION ---")
print(f"Video FPS: {fps:.2f}")
print(f"Total Frames: {int(frame_count)}")
print(f"Video Duration: {duration_seconds:.2f} seconds")


# ------------------------------------------------------------
# 3. YOLOv8 + ByteTrack
# ------------------------------------------------------------

print("\nStarting YOLOv8 + ByteTrack analysis...")

results = model.track(
    source=VIDEO_PATH,
    tracker="bytetrack.yaml",
    save=True,
    conf=0.4,
    stream=True,
    verbose=False
)


# ------------------------------------------------------------
# 4. VEHICLE TRACKING
# ------------------------------------------------------------

vehicle_ids = set()
queue_ids = set()

# COCO classes:
# 2 = car
# 3 = motorcycle
# 5 = bus
# 7 = truck

vehicle_classes = {2, 3, 5, 7}

frames_processed = 0


for result in results:

    frames_processed += 1

    if result.boxes.id is None:
        continue

    boxes = result.boxes.xyxy.cpu().tolist()
    ids = result.boxes.id.int().cpu().tolist()
    classes = result.boxes.cls.int().cpu().tolist()

    frame_height = result.orig_shape[0]

    for box, vehicle_id, class_id in zip(boxes, ids, classes):

        if class_id not in vehicle_classes:
            continue

        x1, y1, x2, y2 = box

        center_y = (y1 + y2) / 2

        vehicle_ids.add(vehicle_id)

        # Lower 40% of frame = approximate queue region
        if center_y > frame_height * 0.60:
            queue_ids.add(vehicle_id)


# ------------------------------------------------------------
# 5. TRAFFIC METRICS
# ------------------------------------------------------------

vehicle_count = len(vehicle_ids)
queue_length = len(queue_ids)


# ------------------------------------------------------------
# 6. TRAFFIC DENSITY
# ------------------------------------------------------------

if vehicle_count < 30:
    density = "Low"
elif vehicle_count < 70:
    density = "Medium"
else:
    density = "High"


# ------------------------------------------------------------
# 7. ADAPTIVE GREEN TIME
# ------------------------------------------------------------

min_green = 20
max_green = 60

queue_factor = queue_length * 0.8

if density == "High":
    density_bonus = 10
elif density == "Medium":
    density_bonus = 5
else:
    density_bonus = 0

green_time = min_green + queue_factor + density_bonus

green_time = max(min_green, min(max_green, green_time))
green_time = round(green_time)


# ------------------------------------------------------------
# 8. SIGNAL DECISION
# ------------------------------------------------------------

if density == "High":
    signal_action = "EXTEND GREEN PHASE"
elif density == "Medium":
    signal_action = "MAINTAIN NORMAL GREEN PHASE"
else:
    signal_action = "REDUCE GREEN PHASE"


# ------------------------------------------------------------
# 9. DISPLAY RESULTS
# ------------------------------------------------------------

print("\n========================================")
print("TRAFFIC ANALYSIS RESULTS")
print("========================================")

print(f"Frames Processed: {frames_processed}")
print(f"Total Unique Vehicles Detected: {vehicle_count}")
print(f"Estimated Queue Vehicles: {queue_length}")
print(f"Traffic Density: {density}")

print("\n========================================")
print("ADAPTIVE SIGNAL DECISION")
print("========================================")

print(f"Recommended Green Time: {green_time} seconds")
print(f"Signal Decision: {signal_action}")

print(
    f"Reason: {density} traffic with "
    f"{queue_length} queued vehicles."
)


# ------------------------------------------------------------
# 10. SAVE ANALYSIS RESULTS
# ------------------------------------------------------------

analysis_results = {
    "case_study": "Oppanakara Street, Coimbatore",

    "video": {
        "fps": round(fps, 2),
        "total_frames": int(frame_count),
        "duration_seconds": round(duration_seconds, 2)
    },

    "traffic_analysis": {
        "frames_processed": frames_processed,
        "vehicles_detected": vehicle_count,
        "queue_length": queue_length,
        "traffic_density": density
    },

    "adaptive_signal": {
        "recommended_green_time": green_time,
        "signal_decision": signal_action
    },

    "technology": {
        "detection": "YOLOv8",
        "tracking": "ByteTrack"
    }
}


os.makedirs("results", exist_ok=True)

output_file = "results/analysis_results.json"

with open(output_file, "w") as file:
    json.dump(analysis_results, file, indent=4)


print("\nAnalysis results saved to:")
print(output_file)

print("\n========================================")
print("SMARTFLOW PIPELINE COMPLETED")
print("========================================")