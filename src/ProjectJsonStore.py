import json
from pathlib import Path


class ProjectJsonStore:
    DATA_DIR = Path(__file__).resolve().parent.parent / "data"
    METRICS_DIR = DATA_DIR / "parsed_files_info"
    WEIGHTS_PATH = DATA_DIR / "weights.json"

    def load_cached_metrics(self, source_path):
        metrics_path = self.METRICS_DIR / f"{Path(source_path).stem}.json"
        if not metrics_path.is_file():
            return None

        with metrics_path.open("r", encoding="utf-8") as metrics_file:
            return json.load(metrics_file)

    def save_metrics(self, source_path, metrics):
        self.METRICS_DIR.mkdir(parents=True, exist_ok=True)
        metrics_path = self.METRICS_DIR / f"{Path(source_path).stem}.json"
        with metrics_path.open("w", encoding="utf-8") as metrics_file:
            json.dump(metrics, metrics_file, indent=4)
        return metrics_path

    def _weights_path(self, network_type):
        if network_type in {"naive", "normal"}:
            return self.WEIGHTS_PATH
        raise ValueError(f"Unknown Bayesian network type: {network_type}")

    def load_weights(self, network_type="naive"):
        weights_path = self._weights_path(network_type)
        with weights_path.open("r", encoding="utf-8") as weights_file:
            stored_weights = json.load(weights_file)

        if "models" in stored_weights:
            if network_type not in stored_weights["models"]:
                raise KeyError(
                    f"No saved weights found for network type: {network_type}"
                )
            return stored_weights["models"][network_type]

        if network_type == "naive":
            return stored_weights
        raise KeyError(f"No saved weights found for network type: {network_type}")

    def save_weights(self, weights, network_type="naive"):
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        weights_path = self._weights_path(network_type)
        stored_weights = {"models": {}}
        if weights_path.is_file():
            with weights_path.open("r", encoding="utf-8") as weights_file:
                existing_weights = json.load(weights_file)
            if "models" in existing_weights:
                stored_weights = existing_weights
            else:
                stored_weights["models"]["naive"] = existing_weights

        stored_weights["models"][network_type] = weights
        with weights_path.open("w", encoding="utf-8") as weights_file:
            json.dump(stored_weights, weights_file, indent=4)
