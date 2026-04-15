"""
FAISS-based Semantic Retrieval Module
Implements fast similarity search using FAISS vector index
"""

import numpy as np
import pandas as pd
import faiss
import logging
import os
from typing import List, Tuple, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FAISSRetriever:
    """
    FAISS-based semantic retrieval system
    Implements PRD Section 7 - Feature 4: FAISS Vector Search Engine
    """
    
    def __init__(self, embedding_dim: int = 768):
        """
        Initialize FAISS retriever
        
        Args:
            embedding_dim: Dimension of embeddings
        """
        self.embedding_dim = embedding_dim
        self.index = None
        self.documents = None
        self.metadata = None
        
        logger.info(f"Initialized FAISS retriever with dimension {embedding_dim}")
    
    def build_index(self, embeddings: np.ndarray, use_gpu: bool = False):
        """
        Build FAISS index from embeddings
        
        Args:
            embeddings: Numpy array of embeddings (n_docs, embedding_dim)
            use_gpu: Whether to use GPU for indexing (if available)
        """
        logger.info(f"Building FAISS index for {len(embeddings)} documents...")
        
        # Ensure embeddings are float32
        embeddings = embeddings.astype('float32')
        
        # Create index (using L2 distance, but embeddings are normalized so it's equivalent to cosine)
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        
        # Optionally move to GPU
        if use_gpu and faiss.get_num_gpus() > 0:
            logger.info("Using GPU for FAISS index")
            res = faiss.StandardGpuResources()
            self.index = faiss.index_cpu_to_gpu(res, 0, self.index)
        
        # Add embeddings to index
        self.index.add(embeddings)
        
        logger.info(f"Index built successfully. Total vectors: {self.index.ntotal}")
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Search for k most similar documents
        
        Args:
            query_embedding: Query embedding vector (1, embedding_dim) or (embedding_dim,)
            k: Number of results to return
            
        Returns:
            Tuple of (distances, indices)
        """
        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")
        
        # Ensure query is 2D and float32
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        query_embedding = query_embedding.astype('float32')
        
        # Search
        distances, indices = self.index.search(query_embedding, k)
        
        return distances[0], indices[0]
    
    def set_documents(self, df: pd.DataFrame):
        """
        Store document metadata for retrieval results
        
        Args:
            df: DataFrame containing document information
        """
        self.documents = df
        logger.info(f"Stored metadata for {len(df)} documents")
    
    def retrieve(self, query_embedding: np.ndarray, k: int = 5) -> pd.DataFrame:
        """
        Retrieve top-k similar documents with metadata
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            DataFrame with retrieved documents and similarity scores
        """
        if self.documents is None:
            raise ValueError("Documents not set. Call set_documents() first.")
        
        distances, indices = self.search(query_embedding, k)
        
        # Get documents
        results = self.documents.iloc[indices].copy()
        
        # Add similarity scores (convert L2 distance to similarity)
        # Since embeddings are normalized, similarity = 1 - (distance^2 / 2)
        similarities = 1 - (distances ** 2) / 2
        results['similarity_score'] = similarities
        results['rank'] = range(1, k + 1)
        
        return results
    
    def save_index(self, output_path: str):
        """
        Save FAISS index to disk
        
        Args:
            output_path: Path to save index
        """
        if self.index is None:
            raise ValueError("No index to save")
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Move to CPU if on GPU (check if GPU support exists)
        try:
            if hasattr(faiss, 'GpuIndex') and isinstance(self.index, faiss.GpuIndex):
                index_cpu = faiss.index_gpu_to_cpu(self.index)
                faiss.write_index(index_cpu, output_path)
            else:
                faiss.write_index(self.index, output_path)
        except:
            # Fallback for CPU-only FAISS
            faiss.write_index(self.index, output_path)
        
        logger.info(f"Saved FAISS index to {output_path}")
    
    def load_index(self, input_path: str, use_gpu: bool = False):
        """
        Load FAISS index from disk
        
        Args:
            input_path: Path to index file
            use_gpu: Whether to load on GPU
        """
        logger.info(f"Loading FAISS index from {input_path}")
        self.index = faiss.read_index(input_path)
        
        if use_gpu and faiss.get_num_gpus() > 0:
            logger.info("Moving index to GPU")
            res = faiss.StandardGpuResources()
            self.index = faiss.index_cpu_to_gpu(res, 0, self.index)
        
        logger.info(f"Index loaded. Total vectors: {self.index.ntotal}")


def build_and_save_index(embeddings_path: str, 
                        data_path: str,
                        output_dir: str = 'models/embeddings',
                        use_gpu: bool = False):
    """
    Build and save FAISS index from embeddings
    
    Args:
        embeddings_path: Path to embeddings .npy file
        data_path: Path to corresponding data CSV
        output_dir: Directory to save index
        use_gpu: Whether to use GPU
        
    Returns:
        FAISSRetriever instance
    """
    # Load embeddings
    logger.info(f"Loading embeddings from {embeddings_path}")
    embeddings = np.load(embeddings_path)
    
    # Load data
    logger.info(f"Loading data from {data_path}")
    df = pd.read_csv(data_path)
    
    # Initialize retriever
    retriever = FAISSRetriever(embedding_dim=embeddings.shape[1])
    
    # Build index
    retriever.build_index(embeddings, use_gpu=use_gpu)
    retriever.set_documents(df)
    
    # Save index
    filename = os.path.splitext(os.path.basename(embeddings_path))[0]
    index_path = os.path.join(output_dir, f'{filename}.index')
    retriever.save_index(index_path)
    
    return retriever


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python retrieval.py <embeddings_path> <data_path>")
        print("Example: python retrieval.py models/embeddings/train_embeddings.npy data/processed/train.csv")
        sys.exit(1)
    
    embeddings_path = sys.argv[1]
    data_path = sys.argv[2]
    
    retriever = build_and_save_index(embeddings_path, data_path)
    
    print("\n" + "="*60)
    print("FAISS INDEX BUILT SUCCESSFULLY")
    print("="*60)
    print(f"Total vectors indexed: {retriever.index.ntotal}")
    print(f"Embedding dimension: {retriever.embedding_dim}")
    print("="*60)
