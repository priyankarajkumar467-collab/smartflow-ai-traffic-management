"""
SMARTFLOW - VALIDATION METRICS

Compares adaptive traffic signal timing against
a fixed 30-second baseline.

Case Study: Oppanakara Street, Coimbatore

Note:
Throughput and queue reduction are prototype estimates,
not real-world measured improvements.
"""

import json
from pathlib import Path


# ============================================================
# FILE PATHS AND CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "results" / "analysis_results.json"
OUTPUT_FILE = BASE_DIR / "results" / "validation_results.json"

FIXED_GREEN_TIME = 30


# ============================================================
# 1. LOAD AI ANALYSIS
# ============================================================

def load_analysis():

    if not INPUT_FILE.is_file():
        raise FileNotFoundError(
            f"Analysis results not found: {INPUT_FILE}\n"
            "Run: python -m ai.vehicle_detection"
        )

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        analysis = json.load(file)

    if not isinstance(analysis, dict):
        raise ValueError("Analysis JSON must contain an object.")

    return analysis


# ============================================================
# 2. EXTRACT AND VALIDATE INPUT DATA
# ============================================================

def extract_analysis_data(analysis):

    try:
        traffic = analysis["analysis"]
        signal = analysis["adaptive_signal"]

        vehicle_count = traffic["unique_vehicles"]
        queue_length = traffic["estimated_queue"]
        density = traffic["traffic_density"]

        green_time = signal["recommended_green_time_seconds"]
        signal_action = signal["signal_decision"]

    except (KeyError, TypeError) as error:
        raise ValueError(
            f"Required analysis data is missing: {error}"
        ) from error

    if (
        not isinstance(vehicle_count, int)
        or isinstance(vehicle_count, bool)
        or vehicle_count < 0
    ):
        raise ValueError("Invalid vehicle count.")

    if (
        not isinstance(queue_length, int)
        or isinstance(queue_length, bool)
        or queue_length < 0
        or queue_length > vehicle_count
    ):
        raise ValueError("Invalid queue length.")

    if density not in ("Low", "Medium", "High"):
        raise ValueError("Invalid traffic density.")

    if (
        not isinstance(green_time, (int, float))
        or isinstance(green_time, bool)
        or green_time <= 0
    ):
        raise ValueError("Invalid adaptive green time.")

    if not isinstance(signal_action, str) or not signal_action:
        raise ValueError("Invalid signal decision.")

    return (
        vehicle_count,
        queue_length,
        density,
        green_time,
        signal_action
    )


# ============================================================
# 3. CALCULATE VALIDATION METRICS
# ============================================================

def calculate_validation_metrics(
    vehicle_count,
    queue_length,
    density,
    green_time
):

    # Estimated throughput
    estimated_throughput = round(
        vehicle_count * (green_time / 60) * 0.60
    )

    # Queue reduction factor
    if density == "High":
        reduction_factor = 0.30

    elif density == "Medium":
        reduction_factor = 0.20

    else:
        reduction_factor = 0.10

    # Estimated queue reduction
    estimated_queue_reduction = round(
        queue_length * reduction_factor
    )

    remaining_queue = max(
        0,
        queue_length - estimated_queue_reduction
    )

    # Queue reduction percentage
    if queue_length > 0:

        queue_reduction_percentage = round(
            (estimated_queue_reduction / queue_length) * 100,
            2
        )

    else:
        queue_reduction_percentage = 0

    # Green-time comparison
    green_time_difference = green_time - FIXED_GREEN_TIME

    green_time_improvement = round(
        (green_time_difference / FIXED_GREEN_TIME) * 100,
        2
    )

    return {
        "estimated_throughput": estimated_throughput,
        "estimated_queue_reduction": estimated_queue_reduction,
        "remaining_queue": remaining_queue,
        "queue_reduction_percentage": queue_reduction_percentage,
        "green_time_difference_seconds": green_time_difference,
        "green_time_improvement_percentage": green_time_improvement
    }


# ============================================================
# 4. CREATE VALIDATION JSON
# ============================================================

def create_validation_result(
    vehicle_count,
    queue_length,
    density,
    green_time,
    signal_action,
    metrics
):

    return {

        "case_study": "Oppanakara Street, Coimbatore",

        "traffic_analysis": {

            "vehicles_detected": vehicle_count,
            "initial_queue": queue_length,
            "traffic_density": density
        },

        "signal_comparison": {

            "fixed_green_time_seconds": FIXED_GREEN_TIME,

            "adaptive_green_time_seconds": green_time,

            "green_time_difference_seconds":
                metrics["green_time_difference_seconds"],

            "green_time_improvement_percentage":
                metrics["green_time_improvement_percentage"],

            "signal_decision": signal_action
        },

        "performance_metrics": {

            "estimated_throughput":
                metrics["estimated_throughput"],

            "estimated_queue_reduction":
                metrics["estimated_queue_reduction"],

            "remaining_queue":
                metrics["remaining_queue"],

            "queue_reduction_percentage":
                metrics["queue_reduction_percentage"]
        },

        "validation_type":
            "Prototype estimation based on AI-detected traffic metrics"
    }


# ============================================================
# 5. DISPLAY RESULTS
# ============================================================

def display_results(
    vehicle_count,
    queue_length,
    density,
    green_time,
    metrics
):

    print("\n" + "=" * 45)
    print("SMARTFLOW VALIDATION RESULTS")
    print("=" * 45)

    print(f"Vehicles Detected        : {vehicle_count}")
    print(f"Initial Queue            : {queue_length}")
    print(f"Traffic Density          : {density}")

    print("\n--- SIGNAL COMPARISON ---")

    print(f"Fixed Green Time         : {FIXED_GREEN_TIME} sec")
    print(f"Adaptive Green Time      : {green_time} sec")

    print("\n--- PERFORMANCE METRICS ---")

    print(
        f"Estimated Throughput     : "
        f"{metrics['estimated_throughput']} vehicles"
    )

    print(
        f"Estimated Queue Reduction: "
        f"{metrics['estimated_queue_reduction']} vehicles"
    )

    print(
        f"Remaining Queue          : "
        f"{metrics['remaining_queue']} vehicles"
    )

    print(
        f"Queue Reduction          : "
        f"{metrics['queue_reduction_percentage']}%"
    )

    print(
        f"Green Time Difference    : "
        f"{metrics['green_time_difference_seconds']} sec"
    )

    print(
        f"Green Time Improvement   : "
        f"{metrics['green_time_improvement_percentage']}%"
    )


# ============================================================
# 6. SAVE RESULTS
# ============================================================

def save_results(validation_results):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            validation_results,
            file,
            indent=4
        )


# ============================================================
# 7. MAIN PROGRAM
# ============================================================

def main():

    try:

        analysis = load_analysis()

        (
            vehicle_count,
            queue_length,
            density,
            green_time,
            signal_action
        ) = extract_analysis_data(analysis)

        metrics = calculate_validation_metrics(
            vehicle_count,
            queue_length,
            density,
            green_time
        )

        validation_results = create_validation_result(
            vehicle_count,
            queue_length,
            density,
            green_time,
            signal_action,
            metrics
        )

        display_results(
            vehicle_count,
            queue_length,
            density,
            green_time,
            metrics
        )

        save_results(validation_results)

        print("\n" + "=" * 45)
        print("VALIDATION COMPLETED")
        print("=" * 45)

        print(f"Results saved to: {OUTPUT_FILE}")

    except (
        FileNotFoundError,
        json.JSONDecodeError,
        ValueError,
        OSError
    ) as error:

        print(f"\nVALIDATION ERROR: {error}")


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()