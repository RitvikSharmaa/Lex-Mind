"""
Legal Document Preprocessing Engine
Handles cleaning, tokenization, normalization for legal texts
"""

import re
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import nltk
from nltk.tokenize import sent_tokenize
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalPreprocessor:
    """
    Preprocessing pipeline for legal documents
    Implements PRD Section 5 preprocessing rules
    """
    
    def __init__(self, max_token_length: int = 512):
        """
        Initialize preprocessor
        
        Args:
            max_token_length: Maximum tokens per document chunk
        """
        self.max_token_length = max_token_length
        self._download_nltk_resources()
    
    def _download_nltk_resources(self):
        """Download required NLTK data"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
    
    def clean_text(self, text: str) -> str:
        """
        Clean legal text following PRD preprocessing rules
        
        Args:
            text: Raw legal document text
            
        Returns:
            Cleaned text
        """
        if pd.isna(text) or not isinstance(text, str):
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalize spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep legal punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\-\(\)]', '', text)
        
        # Lowercase conversion
        text = text.lower()
        
        # Strip whitespace
        text = text.strip()
        
        return text
    
    def tokenize_sentences(self, text: str) -> List[str]:
        """
        Tokenize text into sentences
        
        Args:
            text: Cleaned text
            
        Returns:
            List of sentences
        """
        if not text:
            return []
        
        sentences = sent_tokenize(text)
        return [s.strip() for s in sentences if s.strip()]
    
    def truncate_text(self, text: str) -> str:
        """
        Truncate text to max token length
        
        Args:
            text: Input text
            
        Returns:
            Truncated text
        """
        words = text.split()
        if len(words) > self.max_token_length:
            return ' '.join(words[:self.max_token_length])
        return text
    
    def validate_schema(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate dataset schema per PRD Section 5
        
        Args:
            df: Input dataframe
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check required columns
        required_cols = ['case_id', 'text', 'label']
        for col in required_cols:
            if col not in df.columns:
                errors.append(f"Missing required column: {col}")
        
        if errors:
            return False, errors
        
        # Validate text column non-empty
        if df['text'].isna().any():
            errors.append("Text column contains null values")
        
        empty_texts = (df['text'].str.strip() == '').sum()
        if empty_texts > 0:
            errors.append(f"Text column contains {empty_texts} empty values")
        
        # Validate labels consistent
        if df['label'].isna().any():
            errors.append("Label column contains null values")
        
        return len(errors) == 0, errors
    
    def preprocess_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Full preprocessing pipeline for legal dataset
        
        Args:
            df: Raw dataframe
            
        Returns:
            Preprocessed dataframe
        """
        logger.info(f"Starting preprocessing for {len(df)} records")
        
        # Remove null values
        initial_count = len(df)
        df = df.dropna(subset=['text', 'label'])
        logger.info(f"Removed {initial_count - len(df)} null records")
        
        # Remove duplicates
        initial_count = len(df)
        df = df.drop_duplicates(subset=['text'])
        logger.info(f"Removed {initial_count - len(df)} duplicate records")
        
        # Clean text
        logger.info("Cleaning text...")
        df['cleaned_text'] = df['text'].apply(self.clean_text)
        
        # Truncate to max length
        logger.info("Truncating text...")
        df['cleaned_text'] = df['cleaned_text'].apply(self.truncate_text)
        
        # Remove empty cleaned texts
        df = df[df['cleaned_text'].str.len() > 0]
        
        logger.info(f"Preprocessing complete. Final records: {len(df)}")
        
        return df
    
    def create_train_test_split(self, df: pd.DataFrame, test_size: float = 0.2, 
                                random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Create train/test split if not provided
        
        Args:
            df: Input dataframe
            test_size: Proportion for test set
            random_state: Random seed
            
        Returns:
            Tuple of (train_df, test_df)
        """
        from sklearn.model_selection import train_test_split
        
        train_df, test_df = train_test_split(
            df, 
            test_size=test_size, 
            random_state=random_state,
            stratify=df['label'] if 'label' in df.columns else None
        )
        
        logger.info(f"Split: {len(train_df)} train, {len(test_df)} test")
        
        return train_df, test_df


def load_and_preprocess_dataset(data_path: str, 
                                output_dir: str = 'data/processed',
                                create_split: bool = True) -> Dict[str, pd.DataFrame]:
    """
    Main function to load and preprocess legal dataset
    
    Args:
        data_path: Path to raw dataset CSV
        output_dir: Directory to save processed data
        create_split: Whether to create train/test split
        
    Returns:
        Dictionary with 'train' and 'test' dataframes
    """
    import os
    
    logger.info(f"Loading dataset from {data_path}")
    
    # Load dataset
    df = pd.read_csv(data_path)
    logger.info(f"Loaded {len(df)} records")
    
    # Initialize preprocessor
    preprocessor = LegalPreprocessor()
    
    # Validate schema
    is_valid, errors = preprocessor.validate_schema(df)
    if not is_valid:
        logger.error("Schema validation failed:")
        for error in errors:
            logger.error(f"  - {error}")
        raise ValueError("Dataset schema validation failed")
    
    logger.info("Schema validation passed")
    
    # Preprocess
    df_processed = preprocessor.preprocess_dataframe(df)
    
    # Create split if needed
    if create_split:
        train_df, test_df = preprocessor.create_train_test_split(df_processed)
    else:
        train_df = df_processed
        test_df = None
    
    # Save processed data
    os.makedirs(output_dir, exist_ok=True)
    
    train_path = os.path.join(output_dir, 'train.csv')
    train_df.to_csv(train_path, index=False)
    logger.info(f"Saved train data to {train_path}")
    
    if test_df is not None:
        test_path = os.path.join(output_dir, 'test.csv')
        test_df.to_csv(test_path, index=False)
        logger.info(f"Saved test data to {test_path}")
    
    result = {'train': train_df}
    if test_df is not None:
        result['test'] = test_df
    
    return result


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python preprocess.py <path_to_dataset.csv>")
        sys.exit(1)
    
    data_path = sys.argv[1]
    result = load_and_preprocess_dataset(data_path)
    
    print("\n=== Preprocessing Summary ===")
    print(f"Train records: {len(result['train'])}")
    if 'test' in result:
        print(f"Test records: {len(result['test'])}")
    print("\nSample record:")
    print(result['train'].iloc[0][['case_id', 'cleaned_text', 'label']])
