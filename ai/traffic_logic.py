"""
SmartFlow - Traffic Logic Module
Case Study: Oppanakara Street, Coimbatore
"""

LOW = "Low"
MEDIUM = "Medium"
HIGH = "High"

MIN_GREEN_TIME = 20
MAX_GREEN_TIME = 60


def classify_traffic_density(vehicle_count):

    if not isinstance(vehicle_count, int) or isinstance(vehicle_count, bool):
        raise ValueError("Vehicle count must be an integer.")

    if vehicle_count < 0:
        raise ValueError("Vehicle count cannot be negative.")

    if vehicle_count < 30:
        return LOW
    elif vehicle_count < 70:
        return MEDIUM
    else:
        return HIGH


def calculate_density(queue_length, unique_vehicles):

    if queue_length < 0 or unique_vehicles < 0:
        raise ValueError("Vehicle counts cannot be negative.")

    if queue_length > unique_vehicles:
        raise ValueError("Queue length cannot exceed unique vehicles.")

    if unique_vehicles == 0:
        return LOW, 0.0

    queue_ratio = (queue_length / unique_vehicles) * 100

    if queue_ratio < 20:
        density = LOW
    elif queue_ratio <= 40:
        density = MEDIUM
    else:
        density = HIGH

    return density, round(queue_ratio, 2)


def calculate_queue_length(queue_ids):

    return len(set(queue_ids))


def calculate_green_time(queue_length, density):

    if not isinstance(queue_length, int) or isinstance(queue_length, bool):
        raise ValueError("Queue length must be an integer.")

    if queue_length < 0:
        raise ValueError("Queue length cannot be negative.")

    if density not in (LOW, MEDIUM, HIGH):
        raise ValueError("Invalid traffic density.")

    queue_factor = queue_length * 0.8

    if density == HIGH:
        density_bonus = 10
    elif density == MEDIUM:
        density_bonus = 5
    else:
        density_bonus = 0

    green_time = MIN_GREEN_TIME + queue_factor + density_bonus

    green_time = max(
        MIN_GREEN_TIME,
        min(green_time, MAX_GREEN_TIME)
    )

    return int(round(green_time))


def determine_signal_action(density):

    if density == HIGH:
        return "EXTEND GREEN PHASE"

    elif density == MEDIUM:
        return "MAINTAIN NORMAL GREEN PHASE"

    elif density == LOW:
        return "REDUCE GREEN PHASE"

    raise ValueError("Invalid traffic density.")