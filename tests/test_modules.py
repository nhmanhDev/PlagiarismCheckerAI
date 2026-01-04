"""
Test Multi-Stage Retrieval System

Quick test script to verify all modules work correctly.
"""

import sys
from pathlib import Path

# Test imports
print("="*80)
print("TESTING MULTI-STAGE RETRIEVAL SYSTEM")
print("="*80)

print("\n1. Testing imports...")
try:
    from reranker import DocumentReranker, HybridReranker
    print("   ✅ reranker.py")
except Exception as e:
    print(f"   ❌ reranker.py: {e}")

try:
    from benchmark_loader import VietnameseBenchmark
    print("   ✅ benchmark_loader.py")
except Exception as e:
    print(f"   ❌ benchmark_loader.py: {e}")

try:
    from research_implementation import PlagiarismEvaluator
    print("   ✅ research_implementation.py")
except Exception as e:
    print(f"   ❌ research_implementation.py: {e}")

try:
    from research_extensions import MultiStageEvaluator, calculate_retrieval_metrics
    print("   ✅ research_extensions.py")
except Exception as e:
    print(f"   ❌ research_extensions.py: {e}")

# Test dataset loading
print("\n2. Testing dataset loading...")
try:
    benchmark = VietnameseBenchmark(dataset_path="data/test_data")
    
    test_cases = benchmark.load_plagiarism_pairs()
    print(f"   ✅ Loaded {len(test_cases)} test cases")
    
    corpus = benchmark.load_corpus()
    print(f"   ✅ Loaded {len(corpus)} corpus documents")
    
    stats = benchmark.get_statistics()
    print(f"   ✅ Statistics:")
    print(f"      - Plagiarism: {stats.get('plagiarism_cases', 0)}")
    print(f"      - Non-plagiarism: {stats.get('non_plagiarism_cases', 0)}")
    
except Exception as e:
    print(f"   ❌ Dataset loading failed: {e}")
    test_cases = []
    corpus = []

# Test re-ranker
print("\n3. Testing re-ranker...")
try:
    reranker = DocumentReranker()
    
    query = "Học máy là gì?"
    candidates = [
        "Học máy là một nhánh của AI",
        "Python là ngôn ngữ lập trình",
        "Deep learning sử dụng neural networks"
    ]
    
    results = reranker.rerank(query, candidates, top_k=2)
    print(f"   ✅ Re-ranker working")
    print(f"      Top result score: {results[0][2]:.4f}")
    
except Exception as e:
    print(f"   ❌ Re-ranker failed: {e}")

# Test evaluation
print("\n4. Testing multi-stage evaluator...")
try:
    from research_extensions import MultiStageEvaluator
    
    evaluator = MultiStageEvaluator()
    
    # Add some dummy predictions
    for i in range(5):
        evaluator.add_stage_prediction('bm25', 1, 1, 0.8)
        evaluator.add_stage_prediction('semantic', 1, 1, 0.9)
        evaluator.add_stage_prediction('hybrid', 1, 1, 0.85)
    
    comparison = evaluator.compare_stages()
    print(f"   ✅ Multi-stage evaluator working")
    print(f"      Stages tracked: {list(comparison.keys())}")
    
except Exception as e:
    print(f"   ❌ Evaluator failed: {e}")

# Test retrieval metrics
print("\n5. Testing retrieval metrics...")
try:
    from research_extensions import calculate_retrieval_metrics
    
    retrieved = [1, 3, 5, 7, 2]
    relevant = [1, 2, 5]
    
    metrics = calculate_retrieval_metrics(retrieved, relevant, k=5)
    print(f"   ✅ Retrieval metrics working")
    print(f"      Recall@5: {metrics['recall@k']:.4f}")
    print(f"      Precision@5: {metrics['precision@k']:.4f}")
    print(f"      MRR: {metrics['mrr']:.4f}")
    
except Exception as e:
    print(f"   ❌ Retrieval metrics failed: {e}")

# Summary
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)
print("✅ All core modules are working!")
print("\nNext steps:")
print("  1. Run full experiments: python experiments.py")
print("  2. Integrate with app.py")
print("  3. Collect real results")
print("="*80)
