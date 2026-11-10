import argparse

from BayesianNetwork import BayesianNetwork
from Evaluator import Evaluator
from InformationPackager import InformationPackager
from ProjectJsonStore import ProjectJsonStore


class BayesianPredictor:
    def __init__(self):
        self.json_store = ProjectJsonStore()
        self.information_packager = InformationPackager(self.json_store)
        self.evaluator = Evaluator(self.json_store, self.information_packager)

    def train(self, network_type="naive"):
        training_data = self.information_packager.package_training_data()
        BayesianNetwork(network_type).train(training_data)
        print(f"{network_type} - training done")

    def evaluate(self, network_type="naive"):
        return self.evaluator.evaluate(network_type)

    def predict(self, file_path, network_type="naive"):
        print(f"Predicting: {file_path}")
        metrics = self.information_packager.package_source_file(file_path)
        prediction = BayesianNetwork(network_type).predict(metrics)
        print(prediction)
        return prediction

    def run(self, mode, network_type="naive", file_path=None):
        if mode == "train":
            self.train(network_type)
        elif mode == "test":
            self.evaluate(network_type)
        elif mode == "predict":
            if not file_path:
                raise ValueError("--file option is required in predict mode")
            self.predict(file_path, network_type)

    def run_cli(self, argv=None):
        parser = argparse.ArgumentParser()
        parser.add_argument("--mode", required=True, choices=["train", "test", "predict"])
        parser.add_argument("--file", help="Path to C++ file")
        parser.add_argument(
            "--network-type",
            choices=["naive", "normal"],
            default="naive",
            help="Bayesian network to train or use for prediction (default: naive)",
        )
        args = parser.parse_args(argv)
        if args.mode == "predict" and not args.file:
            parser.error("--file option is required in predict mode")

        self.run(args.mode, args.network_type, args.file)


def main(argv=None):
    BayesianPredictor().run_cli(argv)

if __name__ == "__main__":
    main()
