from ProjectJsonStore import ProjectJsonStore


class BayesianNetwork:
    metrics = ["comment_percentage","cyclomatic_complexity","const_keyword_count","constant_count"]
    categories = ["bad", "medium", "good"]
    levels = range(1, 6)
    normal_parents = {
        "cyclomatic_complexity": ["level", "comment_percentage"],
        "const_keyword_count": ["level", "constant_count"],
        "constant_count": ["level"],
        "comment_percentage": ["level"]
    }

    def __init__(self, mode="naive"):
        self.json_store = ProjectJsonStore()
        self.mode = mode

    @staticmethod
    def calculate_prior_naive(training_data, score):
        favorable_cout = 0
        for file_data in training_data:
            if file_data[1] == score:
                favorable_cout += 1
        return favorable_cout / len(training_data)

    def calculate_probability_naive(self, training_data, target_level, target_metric, target_category):
        favorable_count = 0
        total_count = 0

        for metrics, grade in training_data:
            if grade == target_level:
                total_count += 1
                if metrics.get(target_metric) == target_category:
                    favorable_count += 1

        return favorable_count / total_count

    def calculate_prior_normal(self, training_data, score):
        return self.calculate_prior_naive(training_data, score)

    def calculate_probability_normal(self, training_data, event, parent_events):
        favorable_count = 0
        total_count = 0

        def check_parent_events_data(metrics, grade):
            for parent_metric, parent_category in parent_events:
                if parent_metric == "level":
                    if grade != parent_category:
                        return False
                elif metrics.get(parent_metric) != parent_category:
                    return False
            return True

        for metrics, grade in training_data:
            if check_parent_events_data(metrics, grade):
                total_count += 1
                if metrics.get(event[0]) == event[1]:
                    favorable_count += 1

        if total_count == 0:
            return 0.0

        return favorable_count / total_count

    def train(self, training_data):
        if self.mode == "naive":
            weights = {"priors": {}, "probabilities": {}}

            for level in self.levels:
                weights["priors"][str(level)] = self.calculate_prior_normal(training_data, level)

            for level in self.levels:
                level_key = str(level)
                weights["probabilities"][level_key] = {}
                for metric in self.metrics:
                    weights["probabilities"][level_key][metric] = {}
                    for category in self.categories:
                        weights["probabilities"][level_key][metric][category] = self.calculate_probability_naive(training_data, level, metric, category)

            self.json_store.save_weights(weights)
        elif self.mode == "normal":
            weights = {"priors": {},"probabilities": {},}

            for level in self.levels:
                weights["priors"][str(level)] = self.calculate_prior_normal(training_data, level)

            for level in self.levels:
                weights["probabilities"][str(level)] = {}

                for metric in self.metrics:
                    weights["probabilities"][str(level)][metric] = {}
                    parent_metrics = []
                    for parent in self.normal_parents[metric]:
                        if parent != "level":
                            parent_metrics.append(parent)

                    parent_combinations = [()]
                    for parent_metric in parent_metrics:
                        next_parent_combinations = []
                        for parent_events in parent_combinations:
                            for parent_category in self.categories:
                                next_parent_combinations.append(parent_events + ((parent_metric, parent_category),))
                        parent_combinations = next_parent_combinations

                    for parent_combination in parent_combinations:
                        parent_values = dict(parent_combination)
                        parent_events = []
                        for parent in self.normal_parents[metric]:
                            if parent == "level":
                                parent_events.append((parent, level))
                            else:
                                parent_events.append((parent, parent_values[parent]))

                        parent_event_keys = []
                        for parent_metric, parent_category in parent_events:
                            parent_event_keys.append(f"{parent_metric}={parent_category}")
                        parent_events_key = "|".join(parent_event_keys)

                        category_probabilities = {}
                        for category in self.categories:
                            category_probabilities[category] = self.calculate_probability_normal(training_data, (metric, category), parent_events)
                        weights["probabilities"][str(level)][metric][parent_events_key] = category_probabilities

            self.json_store.save_weights(weights, self.mode)


    def predict(self, metrics_data):
        if self.mode == "naive":
            weights = self.json_store.load_weights()
            predicted_level = 0
            max_probability = 0.0

            for level in self.levels:
                level_string = str(level)
                probability = weights.get("priors").get(level_string)
                probabilities = weights.get("probabilities").get(level_string)
                for metric_name, metric_value in metrics_data.items():
                    metric_probabilities = probabilities.get(metric_name)
                    probability *= metric_probabilities.get(metric_value, 0.0)
                if probability > max_probability:
                    max_probability = probability
                    predicted_level = level

            return predicted_level
        elif self.mode == "normal":
            weights = self.json_store.load_weights(self.mode)
            predicted_level = 0
            max_probability = 0.0
            parents = self.normal_parents

            for level in self.levels:
                level_string = str(level)
                probability = weights["priors"].get(level_string, 0.0)
                probabilities = weights["probabilities"].get(level_string, {})
                for metric_name, metric_value in metrics_data.items():
                    parent_events = []
                    for parent in parents[metric_name]:
                        if parent == "level":
                            parent_events.append((parent, level))
                        else:
                            parent_events.append((parent, metrics_data[parent]))

                    parent_event_keys = []
                    for parent, parent_value in parent_events:
                        parent_event_keys.append(f"{parent}={parent_value}")
                    parent_events_key = "|".join(parent_event_keys)
                    metric_probabilities = probabilities.get(metric_name)
                    parent_probabilities = metric_probabilities.get(parent_events_key)
                    probability *= parent_probabilities.get(metric_value)

                if probability > max_probability:
                    max_probability = probability
                    predicted_level = level

            return predicted_level
