"""
Research Implementation: Vietnamese Sentence Paraphrase Detection

Based on: "Vietnamese Sentence Paraphrase Identification Using Sentence-BERT and PhoBERT" (2024)
Achievement: 95.33% accuracy, 95.42% F1 score

This module implements evaluation metrics and experimental framework
for plagiarism detection research validation.
"""

import numpy as np
from typing import List, Dict, Tuple, Any
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import json


class PlagiarismEvaluator:
\t"""Evaluation framework for plagiarism detection systems."""
\t
\tdef __init__(self):
\t\tself.predictions = []
\t\tself.ground_truth = []
\t\tself.scores = []
\t
\tdef add_prediction(self, predicted_label: int, true_label: int, score: float):
\t\t"""
\t\tAdd a prediction for evaluation.
\t\t
\t\tArgs:
\t\t\tpredicted_label: 1 for plagiarism, 0 for no plagiarism
\t\t\ttrue_label: 1 for plagiarism, 0 for no plagiarism  
\t\t\tscore: Confidence score [0, 1]
\t\t"""
\t\tself.predictions.append(predicted_label)
\t\tself.ground_truth.append(true_label)
\t\tself.scores.append(score)
\t
\tdef calculate_metrics(self) -> Dict[str, float]:
\t\t"""Calculate precision, recall, F1, and AUC."""
\t\tif not self.predictions:
\t\t\treturn {}
\t\t
\t\tmetrics = {
\t\t\t"precision": precision_score(self.ground_truth, self.predictions, zero_division=0),
\t\t\t"recall": recall_score(self.ground_truth, self.predictions, zero_division=0),
\t\t\t"f1_score": f1_score(self.ground_truth, self.predictions, zero_division=0),
\t\t}
\t\t
\t\t# AUC only if we have both classes
\t\tif len(set(self.ground_truth)) > 1:
\t\t\tmetrics["auc"] = roc_auc_score(self.ground_truth, self.scores)
\t\telse:
\t\t\tmetrics["auc"] = 0.0
\t\t
\t\t# Confusion matrix
\t\tcm = confusion_matrix(self.ground_truth, self.predictions)
\t\tif cm.shape == (2, 2):
\t\t\ttn, fp, fn, tp = cm.ravel()
\t\t\tmetrics["true_positives"] = int(tp)
\t\t\tmetrics["true_negatives"] = int(tn)
\t\t\tmetrics["false_positives"] = int(fp)
\t\t\tmetrics["false_negatives"] = int(fn)
\t\t\tmetrics["accuracy"] = (tp + tn) / (tp + tn + fp + fn)
\t\t
\t\treturn metrics
\t
\tdef reset(self):
\t\t"""Reset all stored predictions."""
\t\tself.predictions = []
\t\tself.ground_truth = []
\t\tself.scores = []
\t
\tdef get_confusion_matrix(self) -> np.ndarray:
\t\t"""Get confusion matrix."""
\t\treturn confusion_matrix(self.ground_truth, self.predictions)
\t
\tdef print_report(self):
\t\t"""Print formatted evaluation report."""
\t\tmetrics = self.calculate_metrics()
\t\t
\t\tprint("=" * 60)
\t\tprint("PLAGIARISM DETECTION EVALUATION REPORT")
\t\tprint("=" * 60)
\t\tprint(f"Total Samples: {len(self.predictions)}")
\t\tprint()
\t\tprint(f"Accuracy:  {metrics.get('accuracy', 0):.4f}")
\t\tprint(f"Precision: {metrics.get('precision', 0):.4f}")
\t\tprint(f"Recall:    {metrics.get('recall', 0):.4f}")
\t\tprint(f"F1 Score:  {metrics.get('f1_score', 0):.4f}")
\t\tprint(f"AUC:       {metrics.get('auc', 0):.4f}")
\t\tprint()
\t\tprint("Confusion Matrix:")
\t\tprint(f"  TP: {metrics.get('true_positives', 0):4d}  |  FP: {metrics.get('false_positives', 0):4d}")
\t\tprint(f"  FN: {metrics.get('false_negatives', 0):4d}  |  TN: {metrics.get('true_negatives', 0):4d}")
\t\tprint("=" * 60)


class ExperimentRunner:
\t"""Run experiments comparing different plagiarism detection approaches."""
\t
\tdef __init__(self):
\t\tself.results = {}
\t
\tdef run_experiment(
\t\tself,
\t\tname: str,
\t\tdetection_function,
\t\ttest_data: List[Tuple[str, str, int]]
\t) -> Dict[str, float]:
\t\t"""
\t\tRun an experiment with a given detection function.
\t\t
\t\tArgs:
\t\t\tname: Experiment name
\t\t\tdetection_function: Function that takes (query, candidate) and returns (is_plagiarism, score)
\t\t\ttest_data: List of (query, candidate, label) tuples
\t\t
\t\tReturns:
\t\t\tMetrics dictionary
\t\t"""
\t\tevaluator = PlagiarismEvaluator()
\t\t
\t\tfor query, candidate, true_label in test_data:
\t\t\tis_plagiarism, score = detection_function(query, candidate)
\t\t\tevaluator.add_prediction(int(is_plagiarism), true_label, score)
\t\t
\t\tmetrics = evaluator.calculate_metrics()
\t\tself.results[name] = metrics
\t\t
\t\tprint(f"\n[Experiment: {name}]")
\t\tevaluator.print_report()
\t\t
\t\treturn metrics
\t
\tdef compare_results(self):
\t\t"""Print comparison of all experiments."""
\t\tif not self.results:
\t\t\tprint("No experiments run yet.")
\t\t\treturn
\t\t
\t\tprint("\n" + "=" * 80)
\t\tprint("EXPERIMENT COMPARISON")
\t\tprint("=" * 80)
\t\tprint(f"{'Method':<30} {'Precision':<12} {'Recall':<12} {'F1':<12} {'AUC':<12}")
\t\tprint("-" * 80)
\t\t
\t\tfor name, metrics in self.results.items():
\t\t\tprint(f"{name:<30} {metrics.get('precision', 0):>11.4f} {metrics.get('recall', 0):>11.4f} "
\t\t\t      f"{metrics.get('f1_score', 0):>11.4f} {metrics.get('auc', 0):>11.4f}")
\t\t
\t\tprint("=" * 80)
\t
\tdef export_results(self, filepath: str):
\t\t"""Export results to JSON file."""
\t\twith open(filepath, 'w', encoding='utf-8') as f:
\t\t\tjson.dump(self.results, f, indent=2, ensure_ascii=False)
\t\tprint(f"Results exported to {filepath}")


def create_test_dataset() -> List[Tuple[str, str, int]]:
\t"""
\tCreate a simple test dataset for Vietnamese plagiarism detection.
\t
\tReturns:
\t\tList of (query, candidate, label) where label is 1 for plagiarism, 0 for not
\t"""
\ttest_data = [
\t\t# Exact matches (plagiarism)
\t\t("Học máy là một nhánh của trí tuệ nhân tạo", 
\t\t "Học máy là một nhánh của trí tuệ nhân tạo", 1),
\t\t
\t\t# Paraphrases (plagiarism)
\t\t("Máy học là lĩnh vực của trí tuệ nhân tạo",
\t\t "Học máy là một nhánh của trí tuệ nhân tạo", 1),
\t\t 
\t\t("Python là ngôn ngữ lập trình phổ biến",
\t\t "Python được coi là ngôn ngữ lập trình rất phổ biến", 1),
\t\t
\t\t# No plagiarism
\t\t("Hôm nay trời đẹp",
\t\t "Tôi thích ăn phở", 0),
\t\t
\t\t("Trí tuệ nhân tạo đang phát triển nhanh",
\t\t "Cây xanh rất quan trọng cho môi trường", 0),
\t]
\t
\treturn test_data


if __name__ == "__main__":
\t# Example usage
\tprint("Research Implementation Module")
\tprint("Vietnamese Paraphrase Detection Evaluation")
\tprint()
\t
\t# Create test dataset
\ttest_data = create_test_dataset()
\tprint(f"Test dataset: {len(test_data)} samples")
\t
\t# Example: Simple evaluator
\tevaluator = PlagiarismEvaluator()
\t
\t# Simulate some predictions
\tfor query, candidate, true_label in test_data:
\t\t# Dummy prediction (you would use your actual model here)
\t\tscore = 0.9 if true_label == 1 else 0.2
\t\tpredicted = 1 if score > 0.5 else 0
\t\tevaluator.add_prediction(predicted, true_label, score)
\t
\tevaluator.print_report()
\t
\tprint("\nNote: This is a demo. Integrate with your plagiarism detection system for actual evaluation.")
