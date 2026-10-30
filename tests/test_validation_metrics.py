import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from validation import validation_metrics


class TestValidationMetrics(unittest.TestCase):

    def setUp(self):
        self.valid_analysis = {
            "analysis": {
                "unique_vehicles": 63,
                "estimated_queue": 18,
                "traffic_density": "Medium"
            },
            "adaptive_signal": {
                "recommended_green_time_seconds": 39,
                "signal_decision": "MAINTAIN NORMAL GREEN PHASE"
            }
        }

    # -----------------------------------------
    # 1. TEST INPUT DATA EXTRACTION
    # -----------------------------------------

    def test_extract_valid_analysis_data(self):
        result = validation_metrics.extract_analysis_data(
            self.valid_analysis
        )

        self.assertEqual(
            result,
            (
                63,
                18,
                "Medium",
                39,
                "MAINTAIN NORMAL GREEN PHASE"
            )
        )

    def test_extract_missing_data(self):
        with self.assertRaises(ValueError):
            validation_metrics.extract_analysis_data({})

    def test_invalid_vehicle_count(self):
        analysis = self.valid_analysis.copy()
        analysis["analysis"] = {
            **self.valid_analysis["analysis"],
            "unique_vehicles": -5
        }

        with self.assertRaises(ValueError):
            validation_metrics.extract_analysis_data(analysis)

    def test_invalid_queue_length(self):
        analysis = self.valid_analysis.copy()
        analysis["analysis"] = {
            **self.valid_analysis["analysis"],
            "estimated_queue": 70
        }

        with self.assertRaises(ValueError):
            validation_metrics.extract_analysis_data(analysis)

    def test_invalid_traffic_density(self):
        analysis = self.valid_analysis.copy()
        analysis["analysis"] = {
            **self.valid_analysis["analysis"],
            "traffic_density": "Very High"
        }

        with self.assertRaises(ValueError):
            validation_metrics.extract_analysis_data(analysis)

    def test_invalid_green_time(self):
        analysis = self.valid_analysis.copy()
        analysis["adaptive_signal"] = {
            **self.valid_analysis["adaptive_signal"],
            "recommended_green_time_seconds": 0
        }

        with self.assertRaises(ValueError):
            validation_metrics.extract_analysis_data(analysis)

    def test_invalid_signal_decision(self):
        analysis = self.valid_analysis.copy()
        analysis["adaptive_signal"] = {
            **self.valid_analysis["adaptive_signal"],
            "signal_decision": ""
        }

        with self.assertRaises(ValueError):
            validation_metrics.extract_analysis_data(analysis)

    # -----------------------------------------
    # 2. TEST VALIDATION CALCULATIONS
    # -----------------------------------------

    def test_medium_traffic_metrics(self):
        result = validation_metrics.calculate_validation_metrics(
            63, 18, "Medium", 39
        )

        self.assertEqual(result["estimated_throughput"], 25)
        self.assertEqual(result["estimated_queue_reduction"], 4)
        self.assertEqual(result["remaining_queue"], 14)
        self.assertEqual(result["queue_reduction_percentage"], 22.22)
        self.assertEqual(result["green_time_difference_seconds"], 9)
        self.assertEqual(result["green_time_improvement_percentage"], 30.0)

    def test_high_traffic_queue_reduction(self):
        result = validation_metrics.calculate_validation_metrics(
            50, 10, "High", 40
        )

        self.assertEqual(result["estimated_queue_reduction"], 3)

    def test_low_traffic_queue_reduction(self):
        result = validation_metrics.calculate_validation_metrics(
            50, 10, "Low", 25
        )

        self.assertEqual(result["estimated_queue_reduction"], 1)

    def test_zero_queue(self):
        result = validation_metrics.calculate_validation_metrics(
            20, 0, "Low", 30
        )

        self.assertEqual(result["estimated_queue_reduction"], 0)
        self.assertEqual(result["remaining_queue"], 0)
        self.assertEqual(result["queue_reduction_percentage"], 0)

    # -----------------------------------------
    # 3. TEST VALIDATION RESULT CREATION
    # -----------------------------------------

    def test_create_validation_result(self):
        metrics = validation_metrics.calculate_validation_metrics(
            63, 18, "Medium", 39
        )

        result = validation_metrics.create_validation_result(
            63,
            18,
            "Medium",
            39,
            "MAINTAIN NORMAL GREEN PHASE",
            metrics
        )

        self.assertEqual(
            result["case_study"],
            "Oppanakara Street, Coimbatore"
        )

        self.assertEqual(
            result["traffic_analysis"]["vehicles_detected"],
            63
        )

        self.assertEqual(
            result["signal_comparison"]["adaptive_green_time_seconds"],
            39
        )

        self.assertEqual(
            result["performance_metrics"]["remaining_queue"],
            14
        )

    # -----------------------------------------
    # 4. TEST JSON FILE OPERATIONS
    # -----------------------------------------

    def test_load_analysis(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "analysis.json"

            with open(input_path, "w", encoding="utf-8") as file:
                json.dump(self.valid_analysis, file)

            with patch.object(
                validation_metrics,
                "INPUT_FILE",
                input_path
            ):
                result = validation_metrics.load_analysis()

            self.assertEqual(result, self.valid_analysis)

    def test_load_missing_analysis_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "missing.json"

            with patch.object(
                validation_metrics,
                "INPUT_FILE",
                input_path
            ):
                with self.assertRaises(FileNotFoundError):
                    validation_metrics.load_analysis()

    def test_load_invalid_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "invalid.json"
            input_path.write_text("{invalid json", encoding="utf-8")

            with patch.object(
                validation_metrics,
                "INPUT_FILE",
                input_path
            ):
                with self.assertRaises(json.JSONDecodeError):
                    validation_metrics.load_analysis()

    def test_save_validation_results(self):
        sample_result = {
            "case_study": "Oppanakara Street, Coimbatore"
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "validation.json"

            with patch.object(
                validation_metrics,
                "OUTPUT_FILE",
                output_path
            ):
                validation_metrics.save_results(sample_result)

            with open(output_path, "r", encoding="utf-8") as file:
                saved_data = json.load(file)

            self.assertEqual(saved_data, sample_result)


if __name__ == "__main__":
    unittest.main()