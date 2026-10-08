import json
import os


# ============================================================
# SMARTFLOW - VALIDATION METRICS
# ============================================================


INPUT_FILE = "results/analysis_results.json"
OUTPUT_FILE = "results/validation_results.json"


# ------------------------------------------------------------
# 1. LOAD ACTUAL AI ANALYSIS
# ------------------------------------------------------------

if not os.path.exists(INPUT_FILE):

    print("ERROR: Analysis results not found.")
    print("Run: py ai/vehicle_detection.py")
    exit()


with open(INPUT_FILE, "r") as file:
    analysis = json.load(file)


# ------------------------------------------------------------
# 2. EXTRACT RESULTS
# ------------------------------------------------------------

vehicle_count = analysis["traffic_analysis"]["vehicles_detected"]

queue_length = analysis["traffic_analysis"]["queue_length"]

density = analysis["traffic_analysis"]["traffic_density"]

green_time = analysis["adaptive_signal"]["recommended_green_time"]

signal_action = analysis["adaptive_signal"]["signal_decision"]


# ------------------------------------------------------------
# 3. FIXED SIGNAL BASELINE
# ------------------------------------------------------------

fixed_green_time = 30


# ------------------------------------------------------------
# 4. ESTIMATED THROUGHPUT
# ------------------------------------------------------------

estimated_throughput = round(
    vehicle_count * (green_time / 60) * 0.60
)


# ------------------------------------------------------------
# 5. ESTIMATED QUEUE REDUCTION
# ------------------------------------------------------------

if density == "High":
    reduction_factor = 0.30

elif density == "Medium":
    reduction_factor = 0.20

else:
    reduction_factor = 0.10


initial_queue = queue_length

estimated_queue_reduction = round(
    initial_queue * reduction_factor
)

remaining_queue = max(
    0,
    initial_queue - estimated_queue_reduction
)


# ------------------------------------------------------------
# 6. QUEUE REDUCTION PERCENTAGE
# ------------------------------------------------------------

if initial_queue > 0:

    queue_reduction_percentage = round(
        (estimated_queue_reduction / initial_queue) * 100,
        2
    )

else:

    queue_reduction_percentage = 0


# ------------------------------------------------------------
# 7. GREEN-TIME IMPROVEMENT
# ------------------------------------------------------------

green_time_difference = green_time - fixed_green_time

green_time_improvement = round(
    (green_time_difference / fixed_green_time) * 100,
    2
)


# ------------------------------------------------------------
# 8. CREATE VALIDATION RESULT
# ------------------------------------------------------------

validation_results = {

    "case_study": "Oppanakara Street, Coimbatore",

    "traffic_analysis": {
        "vehicles_detected": vehicle_count,
        "initial_queue": initial_queue,
        "traffic_density": density
    },

    "signal_comparison": {
        "fixed_green_time_seconds": fixed_green_time,
        "adaptive_green_time_seconds": green_time,
        "green_time_difference_seconds": green_time_difference,
        "green_time_improvement_percentage": green_time_improvement,
        "signal_decision": signal_action
    },

    "performance_metrics": {
        "estimated_throughput": estimated_throughput,
        "estimated_queue_reduction": estimated_queue_reduction,
        "remaining_queue": remaining_queue,
        "queue_reduction_percentage": queue_reduction_percentage
    },

    "validation_type": "Prototype estimation based on AI-detected traffic metrics"
}


# ------------------------------------------------------------
# 9. DISPLAY VALIDATION RESULTS
# ------------------------------------------------------------

print("\n========================================")
print("SMARTFLOW VALIDATION RESULTS")
print("========================================")

print(f"Vehicles Detected       : {vehicle_count}")
print(f"Initial Queue           : {initial_queue}")
print(f"Traffic Density         : {density}")

print("\n--- SIGNAL COMPARISON ---")

print(f"Fixed Green Time        : {fixed_green_time} sec")
print(f"Adaptive Green Time     : {green_time} sec")

print("\n--- PERFORMANCE METRICS ---")

print(f"Estimated Throughput    : {estimated_throughput} vehicles")

print(
    f"Estimated Queue Reduction: "
    f"{estimated_queue_reduction} vehicles"
)

print(f"Remaining Queue         : {remaining_queue} vehicles")

print(
    f"Queue Reduction         : "
    f"{queue_reduction_percentage}%"
)

print(
    f"Green Time Difference   : "
    f"{green_time_difference} sec"
)

print(
    f"Green Time Improvement  : "
    f"{green_time_improvement}%"
)


# ------------------------------------------------------------
# 10. SAVE VALIDATION RESULTS
# ------------------------------------------------------------

os.makedirs("results", exist_ok=True)

with open(OUTPUT_FILE, "w") as file:

    json.dump(
        validation_results,
        file,
        indent=4
    )


print("\n========================================")
print("VALIDATION COMPLETED")
print("========================================")

print(f"Results saved to: {OUTPUT_FILE}")