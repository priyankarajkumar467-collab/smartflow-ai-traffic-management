import unittest

from ai.traffic_logic import (
    LOW,
    MEDIUM,
    HIGH,
    classify_traffic_density,
    calculate_queue_length,
    calculate_green_time,
    determine_signal_action
)


class TestTrafficLogic(unittest.TestCase):

    # Test traffic density classification
    def test_low_density(self):
        self.assertEqual(classify_traffic_density(10), LOW)

    def test_medium_density(self):
        self.assertEqual(classify_traffic_density(45), MEDIUM)

    def test_high_density(self):
        self.assertEqual(classify_traffic_density(75), HIGH)

    def test_density_boundary(self):
        self.assertEqual(classify_traffic_density(30), MEDIUM)
        self.assertEqual(classify_traffic_density(70), HIGH)

    def test_negative_vehicle_count(self):
        with self.assertRaises(ValueError):
            classify_traffic_density(-5)

    # Test queue length
    def test_queue_length(self):
        queue_ids = [101, 102, 103, 104]
        self.assertEqual(calculate_queue_length(queue_ids), 4)

    def test_duplicate_queue_ids(self):
        queue_ids = [101, 102, 102, 103]
        self.assertEqual(calculate_queue_length(queue_ids), 3)

    # Test green time calculation
    def test_green_time(self):
        self.assertEqual(calculate_green_time(5, MEDIUM), 29)

    def test_minimum_green_time(self):
        self.assertEqual(calculate_green_time(0, LOW), 20)

    def test_maximum_green_time(self):
        self.assertEqual(calculate_green_time(100, HIGH), 60)

    def test_negative_queue_length(self):
        with self.assertRaises(ValueError):
            calculate_green_time(-5, MEDIUM)

    def test_invalid_density(self):
        with self.assertRaises(ValueError):
            calculate_green_time(5, "Invalid")

    # Test signal decisions
    def test_high_density_signal(self):
        self.assertEqual(
            determine_signal_action(HIGH),
            "EXTEND GREEN PHASE"
        )

    def test_medium_density_signal(self):
        self.assertEqual(
            determine_signal_action(MEDIUM),
            "MAINTAIN NORMAL GREEN PHASE"
        )

    def test_low_density_signal(self):
        self.assertEqual(
            determine_signal_action(LOW),
            "REDUCE GREEN PHASE"
        )

    def test_invalid_signal_density(self):
        with self.assertRaises(ValueError):
            determine_signal_action("Invalid")


if __name__ == "__main__":
    unittest.main()