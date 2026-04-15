"""
Download and prepare models for deployment
"""
import os
import pandas as pd
from src.embedder import LegalEmbedder
from src.retrieval import FAISSRetriever

def setup_models():
    """Download models and create embeddings if they don't exist"""
    print("Setting up models...")
    
    # Create directories if they don't exist
    os.makedirs('models/embeddings', exist_ok=True)
    
    # Check if embeddings exist
    if not os.path.exists('models/embeddings/train_embeddings.index'):
        print("Embeddings not found. Creating them...")
        
        # Load data
        if not os.path.exists('data/processed/train.csv'):
            print("ERROR: train.csv not found!")
            return False
            
        train_df = pd.read_csv('data/processed/train.csv')
        print(f"Loaded {len(train_df)} documents")
        
        # Initialize embedder
        embedder = LegalEmbedder()
        
        # Create embeddings
        print("Encoding documents (this may take a while)...")
        texts = train_df['text'].tolist()
        embeddings = embedder.encode_texts(texts)
        
        # Create and save FAISS index
        print("Creating FAISS index...")
        retriever = FAISSRetriever(embedding_dim=768)
        retriever.build_index(embeddings)
        retriever.save_index('models/embeddings/train_embeddings.index')
        
        print("Embeddings created successfully!")
    else:
        print("Embeddings already exist.")
    
    return True

if __name__ == '__main__':
    success = setup_models()
    if not success:
        print("Failed to setup models")
        exit(1)
    print("Setup complete!")
