"""
Embedding Generation Module
Uses sentence-transformers to generate dense embeddings for legal documents
"""

import pandas as pd
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from typing import List, Optional
import logging
import os
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LegalEmbedder:
    """
    Generates embeddings for legal documents using sentence-transformers
    Implements PRD Section 7 - Model A: Embedding Generator
    """
    
    def __init__(self, model_name: str = 'sentence-transformers/all-mpnet-base-v2',
                 device: Optional[str] = None):
        """
        Initialize embedding model
        
        Args:
            model_name: HuggingFace model identifier
            device: Device to use ('cuda', 'cpu', or None for auto-detect)
        """
        self.model_name = model_name
        
        # Auto-detect device if not specified
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
        
        logger.info(f"Loading embedding model: {model_name}")
        logger.info(f"Using device: {self.device}")
        
        # Load model
        self.model = SentenceTransformer(model_name, device=self.device)
        
        # Get embedding dimension
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"Embedding dimension: {self.embedding_dim}")
    
    def encode_texts(self, texts: List[str], batch_size: int = 32,
                     show_progress: bool = True) -> np.ndarray:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings to embed
            batch_size: Batch size for encoding
            show_progress: Whether to show progress bar
            
        Returns:
            Numpy array of embeddings (n_texts, embedding_dim)
        """
        logger.info(f"Encoding {len(texts)} texts...")
        
        # Generate embeddings
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
            normalize_embeddings=True  # L2 normalization for cosine similarity
        )
        
        logger.info(f"Generated embeddings shape: {embeddings.shape}")
        return embeddings
    
    def encode_dataframe(self, df: pd.DataFrame, text_column: str = 'cleaned_text',
                        batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for texts in a DataFrame
        
        Args:
            df: DataFrame containing texts
            text_column: Name of column containing text
            batch_size: Batch size for encoding
            
        Returns:
            Numpy array of embeddings
        """
        if text_column not in df.columns:
            raise ValueError(f"Column '{text_column}' not found in DataFrame")
        
        texts = df[text_column].tolist()
        return self.encode_texts(texts, batch_size=batch_size)
    
    def save_embeddings(self, embeddings: np.ndarray, output_path: str):
        """
        Save embeddings to disk
        
        Args:
            embeddings: Numpy array of embeddings
            output_path: Path to save embeddings (.npy file)
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        np.save(output_path, embeddings)
        logger.info(f"Saved embeddings to {output_path}")
    
    def load_embeddings(self, input_path: str) -> np.ndarray:
        """
        Load embeddings from disk
        
        Args:
            input_path: Path to embeddings file (.npy)
            
        Returns:
            Numpy array of embeddings
        """
        embeddings = np.load(input_path)
        logger.info(f"Loaded embeddings from {input_path}")
        logger.info(f"Shape: {embeddings.shape}")
        return embeddings


def generate_and_save_embeddings(data_path: str, 
                                 output_dir: str = 'models/embeddings',
                                 text_column: str = 'cleaned_text',
                                 batch_size: int = 32):
    """
    Main function to generate and save embeddings for a dataset
    
    Args:
        data_path: Path to CSV file with preprocessed data
        output_dir: Directory to save embeddings
        text_column: Column name containing text
        batch_size: Batch size for encoding
        
    Returns:
        Tuple of (embeddings, dataframe)
    """
    logger.info(f"Loading data from {data_path}")
    df = pd.read_csv(data_path)
    logger.info(f"Loaded {len(df)} records")
    
    # Initialize embedder
    embedder = LegalEmbedder()
    
    # Generate embeddings
    embeddings = embedder.encode_dataframe(df, text_column=text_column, 
                                          batch_size=batch_size)
    
    # Save embeddings
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract filename without extension
    filename = os.path.splitext(os.path.basename(data_path))[0]
    output_path = os.path.join(output_dir, f'{filename}_embeddings.npy')
    
    embedder.save_embeddings(embeddings, output_path)
    
    # Save metadata
    metadata = {
        'model': embedder.model_name,
        'embedding_dim': embedder.embedding_dim,
        'num_documents': len(df),
        'text_column': text_column
    }
    
    metadata_path = os.path.join(output_dir, f'{filename}_metadata.txt')
    with open(metadata_path, 'w') as f:
        for key, value in metadata.items():
            f.write(f"{key}: {value}\n")
    
    logger.info(f"Saved metadata to {metadata_path}")
    
    return embeddings, df


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python embedder.py <path_to_csv>")
        print("Example: python embedder.py data/processed/train.csv")
        sys.exit(1)
    
    data_path = sys.argv[1]
    embeddings, df = generate_and_save_embeddings(data_path)
    
    print("\n" + "="*60)
    print("EMBEDDING GENERATION COMPLETE")
    print("="*60)
    print(f"Documents processed: {len(df)}")
    print(f"Embedding dimension: {embeddings.shape[1]}")
    print(f"Total embeddings: {embeddings.shape[0]}")
    print("="*60)
