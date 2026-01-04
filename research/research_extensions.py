# Multi-Stage Retrieval Extensions for research_implementation.py
# Append these classes and functions to research_implementation.py

from typing import Dict, List

class MultiStageEvaluator(PlagiarismEvaluator):
    """Evaluator for multi-stage retrieval systems."""
    
    def __init__(self):
        super().__init__()
        self.stage_results = {
            'bm25': {'predictions': [], 'ground_truth': [], 'scores': []},
            'semantic': {'predictions': [], 'ground_truth': [], 'scores': []},
            'hybrid': {'predictions': [], 'ground_truth': [], 'scores': []},
            'reranked': {'predictions': [], 'ground_truth': [], 'scores': []}
        }
    
    def add_stage_prediction(self, stage_name: str, predicted_label: int, true_label: int, score: float):
        """Add prediction for a specific stage."""
        if stage_name not in self.stage_results:
            raise ValueError(f"Unknown stage: {stage_name}")
        
        self.stage_results[stage_name]['predictions'].append(predicted_label)
        self.stage_results[stage_name]['ground_truth'].append(true_label)
        self.stage_results[stage_name]['scores'].append(score)
    
    def calculate_stage_metrics(self, stage_name: str) -> Dict[str, float]:
        """Calculate metrics for a specific stage."""
        if stage_name not in self.stage_results:
            raise ValueError(f"Unknown stage: {stage_name}")
        
        data = self.stage_results[stage_name]
        
        if not data['predictions']:
            return {}
        
        from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
        
        metrics = {
            "precision": precision_score(data['ground_truth'], data['predictions'], zero_division=0),
            "recall": recall_score(data['ground_truth'], data['predictions'], zero_division=0),
            "f1_score": f1_score(data['ground_truth'], data['predictions'], zero_division=0),
        }
        
        if len(set(data['ground_truth'])) > 1:
            metrics["auc"] = roc_auc_score(data['ground_truth'], data['scores'])
        else:
            metrics["auc"] = 0.0
        
        cm = confusion_matrix(data['ground_truth'], data['predictions'])
        if cm.shape == (2, 2):
            tn, fp, fn, tp = cm.ravel()
            metrics["accuracy"] = (tp + tn) / (tp + tn + fp + fn)
        
        return metrics
    
    def compare_stages(self) -> Dict[str, Dict[str, float]]:
        """Compare metrics across all stages."""
        comparison = {}
        
        for stage_name in self.stage_results.keys():
            if self.stage_results[stage_name]['predictions']:
                comparison[stage_name] = self.calculate_stage_metrics(stage_name)
        
        return comparison
    
    def print_comparison(self):
        """Print comparison of all stages."""
        comparison = self.compare_stages()
        
        if not comparison:
            print("No stage results available")
            return
        
        print("\n" + "=" * 80)
        print("MULTI-STAGE RETRIEVAL COMPARISON")
        print("=" * 80)
        print(f"{'Stage':<15} {'Precision':<12} {'Recall':<12} {'F1':<12} {'AUC':<12}")
        print("-" * 80)
        
        for stage_name, metrics in comparison.items():
            print(f"{stage_name:<15} {metrics.get('precision', 0):>11.4f} "
                  f"{metrics.get('recall', 0):>11.4f} {metrics.get('f1_score', 0):>11.4f} "
                  f"{metrics.get('auc', 0):>11.4f}")
        
        print("=" * 80)


def calculate_retrieval_metrics(retrieved_docs: List[int], relevant_docs: List[int], k: int = 10) -> Dict[str, float]:
    """Calculate retrieval-specific metrics (Recall@K, Precision@K, MRR, MAP)."""
    retrieved_set = set(retrieved_docs[:k])
    relevant_set = set(relevant_docs)
    
    if not relevant_set:
        return {'recall@k': 0.0, 'precision@k': 0.0, 'mrr': 0.0, 'map': 0.0}
    
    recall_at_k = len(retrieved_set & relevant_set) / len(relevant_set)
    precision_at_k = len(retrieved_set & relevant_set) / k if k > 0 else 0.0
    
    # MRR
    mrr = 0.0
    for rank, doc_id in enumerate(retrieved_docs, 1):
        if doc_id in relevant_set:
            mrr = 1.0 / rank
            break
    
    # MAP
    precisions = []
    num_relevant = 0
    for rank, doc_id in enumerate(retrieved_docs, 1):
        if doc_id in relevant_set:
            num_relevant += 1
            precisions.append(num_relevant / rank)
    
    avg_precision = sum(precisions) / len(relevant_set) if precisions else 0.0
    
    return {
        'recall@k': recall_at_k,
        'precision@k': precision_at_k,
        'mrr': mrr,
        'map': avg_precision
    }
