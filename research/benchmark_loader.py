"""
Benchmark Dataset Loader for Vietnamese Plagiarism Detection

This module provides utilities for loading and managing benchmark datasets
for evaluating plagiarism detection systems.

Supports:
- Vietnamese academic corpus
- Plagiarism test cases with ground truth
- Multiple dataset formats
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)


class VietnameseBenchmark:
    """
    Benchmark dataset loader for Vietnamese plagiarism detection.
    """
    
    def __init__(self, dataset_path: Optional[str] = None):
        """
        Initialize benchmark loader.
        
        Args:
            dataset_path: Path to dataset directory or file
        """
        self.dataset_path = Path(dataset_path) if dataset_path else None
        self.corpus_documents: List[str] = []
        self.test_cases: List[Dict[str, Any]] = []
    
    def load_plagiarism_pairs(
        self,
        filepath: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Load plagiarism test cases with ground truth.
        
        Expected format (JSON):
        [
            {
                "query": "text to check",
                "source": "original text",
                "label": 1,  # 1 for plagiarism, 0 for not
                "similarity": 0.85  # optional
            },
            ...
        ]
        
        Args:
            filepath: Path to test cases file (JSON or CSV)
        
        Returns:
            List of test case dictionaries
        """
        if filepath is None:
            if self.dataset_path is None:
                logger.warning("No dataset path provided")
                return []
            filepath = self.dataset_path / "test_cases.json"
        else:
            filepath = Path(filepath)
        
        if not filepath.exists():
            logger.warning(f"Test cases file not found: {filepath}")
            return self._create_sample_test_cases()
        
        # Load based on file extension
        if filepath.suffix == '.json':
            with open(filepath, 'r', encoding='utf-8') as f:
                test_cases = json.load(f)
        elif filepath.suffix == '.csv':
            test_cases = self._load_csv(filepath)
        else:
            raise ValueError(f"Unsupported file format: {filepath.suffix}")
        
        self.test_cases = test_cases
        logger.info(f"Loaded {len(test_cases)} test cases from {filepath}")
        
        return test_cases
    
    def load_corpus(
        self,
        filepath: Optional[str] = None
    ) -> List[str]:
        """
        Load reference corpus documents.
        
        Args:
            filepath: Path to corpus file (text file, one document per line)
        
        Returns:
            List of document texts
        """
        if filepath is None:
            if self.dataset_path is None:
                logger.warning("No dataset path provided")
                return []
            filepath = self.dataset_path / "corpus.txt"
        else:
            filepath = Path(filepath)
        
        if not filepath.exists():
            logger.warning(f"Corpus file not found: {filepath}")
            return self._create_sample_corpus()
        
        with open(filepath, 'r', encoding='utf-8') as f:
            documents = [line.strip() for line in f if line.strip()]
        
        self.corpus_documents = documents
        logger.info(f"Loaded {len(documents)} documents from corpus")
        
        return documents
    
    def _load_csv(self, filepath: Path) -> List[Dict[str, Any]]:
        """Load test cases from CSV file."""
        test_cases = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                test_case = {
                    'query': row['query'],
                    'source': row['source'],
                    'label': int(row['label']),
                }
                if 'similarity' in row:
                    test_case['similarity'] = float(row['similarity'])
                test_cases.append(test_case)
        
        return test_cases
    
    def _create_sample_test_cases(self) -> List[Dict[str, Any]]:
        """Create sample test cases for demo purposes."""
        logger.info("Creating sample test cases")
        
        return [
            {
                "query": "Học máy là một nhánh của trí tuệ nhân tạo",
                "source": "Học máy là một nhánh của trí tuệ nhân tạo",
                "label": 1,
                "similarity": 1.0,
                "description": "Exact copy"
            },
            {
                "query": "Machine learning thuộc về AI",
                "source": "Học máy là một nhánh của trí tuệ nhân tạo",
                "label": 1,
                "similarity": 0.85,
                "description": "Paraphrased (Eng-Vie)"
            },
            {
                "query": "Máy học giúp máy tính học từ dữ liệu",
                "source": "Học máy là một nhánh của trí tuệ nhân tạo",
                "label": 1,
                "similarity": 0.75,
                "description": "Paraphrased"
            },
            {
                "query": "Hôm nay trời đẹp",
                "source": "Tôi thích ăn phở",
                "label": 0,
                "similarity": 0.1,
                "description": "Unrelated"
            },
            {
                "query": "Python là ngôn ngữ lập trình phổ biến",
                "source": "JavaScript được sử dụng rộng rãi trong web",
                "label": 0,
                "similarity": 0.3,
                "description": "Related but not plagiarism"
            }
        ]
    
    def _create_sample_corpus(self) -> List[str]:
        """Create sample corpus for demo purposes."""
        logger.info("Creating sample corpus")
        
        return [
            "Học máy là một nhánh của trí tuệ nhân tạo.",
            "Python là ngôn ngữ lập trình phổ biến nhất hiện nay.",
            "Xử lý ngôn ngữ tự nhiên giúp máy tính hiểu văn bản.",
            "Deep learning sử dụng mạng neural nhiều tầng.",
            "Trí tuệ nhân tạo đang phát triển rất nhanh.",
            "JavaScript là ngôn ngữ cho web development.",
            "Data science kết hợp thống kê và lập trình.",
            "Computer vision giúp máy tính nhìn như con người.",
            "Cloud computing cung cấp tài nguyên trên mạng.",
            "Blockchain là công nghệ phân tán và bảo mật."
        ]
    
    def save_test_cases(self, filepath: str, test_cases: Optional[List[Dict]] = None):
        """
        Save test cases to file.
        
        Args:
            filepath: Output file path
            test_cases: Test cases to save (uses self.test_cases if None)
        """
        if test_cases is None:
            test_cases = self.test_cases
        
        filepath = Path(filepath)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(test_cases, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(test_cases)} test cases to {filepath}")
    
    def save_corpus(self, filepath: str, documents: Optional[List[str]] = None):
        """
        Save corpus to file.
        
        Args:
            filepath: Output file path
            documents: Documents to save (uses self.corpus_documents if None)
        """
        if documents is None:
            documents = self.corpus_documents
        
        filepath = Path(filepath)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            for doc in documents:
                f.write(doc + '\n')
        
        logger.info(f"Saved {len(documents)} documents to {filepath}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the loaded dataset."""
        stats = {
            'num_test_cases': len(self.test_cases),
            'num_corpus_documents': len(self.corpus_documents),
        }
        
        if self.test_cases:
            plagiarism_count = sum(1 for tc in self.test_cases if tc.get('label') == 1)
            stats['plagiarism_cases'] = plagiarism_count
            stats['non_plagiarism_cases'] = len(self.test_cases) - plagiarism_count
            stats['plagiarism_ratio'] = plagiarism_count / len(self.test_cases)
        
        return stats
    
    def print_statistics(self):
        """Print dataset statistics."""
        stats = self.get_statistics()
        
        print("=== Dataset Statistics ===")
        print(f"Test cases: {stats['num_test_cases']}")
        if 'plagiarism_cases' in stats:
            print(f"  - Plagiarism: {stats['plagiarism_cases']}")
            print(f"  - Non-plagiarism: {stats['non_plagiarism_cases']}")
            print(f"  - Ratio: {stats['plagiarism_ratio']:.2%}")
        print(f"Corpus documents: {stats['num_corpus_documents']}")


def demo():
    """Demo usage of benchmark loader."""
    print("=== Benchmark Loader Demo ===\n")
    
    # Create loader
    benchmark = VietnameseBenchmark()
    
    # Load sample data
    test_cases = benchmark.load_plagiarism_pairs()
    corpus = benchmark.load_corpus()
    
    # Show statistics
    benchmark.print_statistics()
    
    # Show sample test case
    print("\n=== Sample Test Case ===")
    if test_cases:
        tc = test_cases[0]
        print(f"Query: {tc['query']}")
        print(f"Source: {tc['source']}")
        print(f"Label: {tc['label']} ({'Plagiarism' if tc['label'] == 1 else 'Not plagiarism'})")
        if 'similarity' in tc:
            print(f"Similarity: {tc['similarity']:.2f}")
    
    # Show sample corpus
    print("\n=== Sample Corpus (first 3) ===")
    for i, doc in enumerate(corpus[:3], 1):
        print(f"{i}. {doc}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    demo()
