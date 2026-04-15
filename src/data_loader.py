"""
Dataset Loading and Validation Module
Handles AILA dataset ingestion with schema validation
"""

import pandas as pd
import os
from typing import Optional, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AILADatasetLoader:
    """
    Loader for AILA FIRE 2019 Legal Dataset
    Implements PRD Section 5 dataset specifications
    """
    
    def __init__(self, data_dir: str = 'data/processed'):
        """
        Initialize dataset loader
        
        Args:
            data_dir: Directory containing processed dataset files
        """
        self.data_dir = data_dir
        self.required_columns = ['case_id', 'text', 'label']
        self.optional_columns = []
    
    def load_dataset(self, filename: str = 'aila_dataset.csv') -> pd.DataFrame:
        """
        Load dataset from CSV file
        
        Args:
            filename: Name of CSV file to load
            
        Returns:
            Loaded dataframe
        """
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Dataset file not found: {filepath}")
        
        logger.info(f"Loading dataset from {filepath}")
        df = pd.read_csv(filepath)
        logger.info(f"Loaded {len(df)} records with {len(df.columns)} columns")
        
        return df
    
    def validate_columns(self, df: pd.DataFrame) -> bool:
        """
        Validate required columns exist
        
        Args:
            df: Input dataframe
            
        Returns:
            True if valid, raises ValueError otherwise
        """
        missing_cols = [col for col in self.required_columns if col not in df.columns]
        
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        logger.info("Column validation passed")
        return True
    
    def get_dataset_info(self, df: pd.DataFrame) -> Dict:
        """
        Get dataset statistics and information
        
        Args:
            df: Input dataframe
            
        Returns:
            Dictionary with dataset info
        """
        info = {
            'total_records': len(df),
            'columns': list(df.columns),
            'null_counts': df.isnull().sum().to_dict(),
            'label_distribution': df['label'].value_counts().to_dict() if 'label' in df.columns else {},
            'avg_text_length': df['text'].str.len().mean() if 'text' in df.columns else 0,
            'duplicate_count': df.duplicated().sum()
        }
        
        return info
    
    def load_all_splits(self) -> Dict[str, pd.DataFrame]:
        """
        Load all available dataset splits (train, test, validation)
        
        Returns:
            Dictionary with available splits
        """
        splits = {}
        
        for split_name in ['train', 'test', 'validation']:
            filepath = os.path.join(self.data_dir, f'{split_name}.csv')
            if os.path.exists(filepath):
                splits[split_name] = pd.read_csv(filepath)
                logger.info(f"Loaded {split_name}: {len(splits[split_name])} records")
        
        if not splits:
            raise FileNotFoundError(f"No dataset files found in {self.data_dir}")
        
        return splits


def setup_data_directories():
    """Create required data directories"""
    directories = [
        'data/raw',
        'data/processed',
        'models/embeddings',
        'models/bert_qa',
        'models/summarizer'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")


if __name__ == "__main__":
    # Setup directories
    setup_data_directories()
    
    # Example usage
    loader = AILADatasetLoader(data_dir='data/processed')
    
    print("\n=== AILA Dataset Loader ===")
    print("Run dataset_converter.py first to convert raw AILA data")
    print("Then load from: data/processed/aila_dataset.csv")
