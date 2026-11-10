import csv
from BayesianNetwork import BayesianNetwork

class Evaluator:
    def __init__(self, json_store, information_packager):
        self.json_store = json_store
        self.information_packager = information_packager

    def evaluate(self, network_type="naive"):
        evaluation_rows = self._load_test_rows()
        if not evaluation_rows:
            raise ValueError("No test rows with valid scores are available to evaluate")

        network = BayesianNetwork(network_type)
        print(f"Evaluating {len(evaluation_rows)} test files - {network_type}")

        correct_predictions = sum(
            self._evaluate_file(network, file_name, actual_score)
            for file_name, actual_score in evaluation_rows
        )

        return self._report_summary(correct_predictions, len(evaluation_rows))

    def _evaluate_file(self, network, file_name, actual_score):
        file_path = self.information_packager.source_dir / file_name
        metrics = self.information_packager.package_source_file(file_path)
        predicted_score = network.predict(metrics)
        is_correct = predicted_score == actual_score
        result = "correct" if is_correct else "incorrect"
        print(f"{file_name}: actual={actual_score}, "f"predicted={predicted_score} ({result})")
        return is_correct

    def _report_summary(self, correct_predictions, evaluated_count):
        accuracy = correct_predictions / evaluated_count
        print(f"Evaluation {correct_predictions}/{evaluated_count} correct "f"({accuracy:.1%} accuracy)")
        return accuracy

    def _load_test_rows(self):
        manifest_path = self.information_packager.dataset_config
        with manifest_path.open(
            mode="r", encoding="utf-8", newline=""
        ) as manifest_file:
            rows = list(csv.DictReader(manifest_file))

        evaluation_rows = []
        for row in rows:
            if (row.get("Status") or "").strip().lower() != "test":
                continue

            parsed_row = self._parse_test_row(row)
            if parsed_row is not None:
                evaluation_rows.append(parsed_row)

        return evaluation_rows

    def _parse_test_row(self, row):
        file_name = (row.get("File Name") or "").strip()
        try:
            score = int((row.get("Score") or "").strip())
        except ValueError:
            score = None

        if not file_name or score not in range(1, 6):
            print(
                f"[Warning] Skipping test row with missing or invalid "
                f"file name/score: {file_name or '<missing file name>'}"
            )
            return None
        return file_name, score
