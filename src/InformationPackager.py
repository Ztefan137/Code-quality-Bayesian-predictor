import csv
from pathlib import Path

from FeatureExtractor import FeatureExtractor
from ProjectJsonStore import ProjectJsonStore


class InformationPackager:
    data_dir = Path(__file__).resolve().parent.parent / "data"
    dataset_config = data_dir / "dataset.csv"
    source_dir = data_dir / "source_files"

    def __init__(self, json_store=None):
        self.json_store = (
            json_store if json_store is not None else ProjectJsonStore()
        )

    def package_training_data(self):
        training_data = []
        with self.dataset_config.open(mode="r", encoding="utf-8", newline="") as manifest_file:
            for row in csv.DictReader(manifest_file):
                if (row.get("Status") or "").strip().lower() != "train":
                    continue

                sample = self._create_training_sample(row)
                if sample is not None:
                    training_data.append(sample)

        return training_data

    def package_source_file(self, source_path):
        raw_metrics = self._load_or_extract_metrics(Path(source_path))
        if not raw_metrics:
            raise ValueError(f"No metrics found for {source_path}")
        return self.categorize_metrics(raw_metrics)

    def _create_training_sample(self, row):
        file_name = (row.get("File Name") or "").strip()
        if not file_name:
            return None

        try:
            grade = int((row.get("Score") or "").strip())
        except ValueError:
            print(f"[Warning] Missing or invalid score for {file_name}")
            return None

        source_path = self.source_dir / file_name
        raw_metrics = self._load_or_extract_metrics(source_path)

        return self.categorize_metrics(raw_metrics), grade

    def _load_or_extract_metrics(self, source_path):
        cached_metrics = self.json_store.load_cached_metrics(source_path)
        if cached_metrics is not None:
            return cached_metrics

        if not source_path.is_file():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        metrics = FeatureExtractor(str(source_path)).extract_all()
        self.json_store.save_metrics(source_path, metrics)
        return metrics

    @staticmethod
    def categorize_metrics(raw_metrics):
        return {
            key: InformationPackager.evaluate_metric(key, value)
            for key, value in raw_metrics.items()
            if isinstance(value, (int, float))
        }

    @staticmethod
    def evaluate_metric(name, value):
        if name == "cyclomatic_complexity":
            if value <= 5:
                return "good"
            if value <= 15:
                return "medium"
            return "bad"
        if name == "comment_percentage":
            if value >= 20.0:
                return "good"
            if value >= 10.0:
                return "medium"
            return "bad"
        if name == "const_keyword_count":
            if value >= 3:
                return "good"
            if value >= 1:
                return "medium"
            return "bad"
        if name == "constant_count":
            if value <= 5:
                return "good"
            if value <= 24:
                return "medium"
            return "bad"
