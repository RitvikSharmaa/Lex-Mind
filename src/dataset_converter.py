"""
AILA Dataset Converter
Converts AILA legal retrieval dataset to structured format for deep learning
"""

import os
import pandas as pd
import logging
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AILADatasetConverter:
    """
    Converts AILA FIRE 2019 dataset to structured CSV format
    """
    
    def __init__(self, raw_data_dir: str = 'data/raw'):
        """
        Initialize converter
        
        Args:
            raw_data_dir: Directory containing AILA dataset
        """
        self.raw_data_dir = raw_data_dir
        self.casedocs_dir = os.path.join(raw_data_dir, 'Object_casedocs')
        self.statutes_dir = os.path.join(raw_data_dir, 'Object_statutes')
        self.query_file = os.path.join(raw_data_dir, 'Query_doc.txt')
    
    def load_case_documents(self) -> pd.DataFrame:
        """
        Load all prior case documents
        
        Returns:
            DataFrame with case_id and text columns
        """
        logger.info("Loading case documents...")
        
        cases = []
        case_files = [f for f in os.listdir(self.casedocs_dir) if f.endswith('.txt')]
        
        for filename in case_files:
            case_id = filename.replace('.txt', '')
            filepath = os.path.join(self.casedocs_dir, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read().strip()
                    if text:
                        cases.append({
                            'case_id': case_id,
                            'text': text,
                            'label': 'prior_case'
                        })
            except Exception as e:
                logger.warning(f"Error reading {filename}: {e}")
        
        logger.info(f"Loaded {len(cases)} case documents")
        return pd.DataFrame(cases)
    
    def load_statutes(self) -> pd.DataFrame:
        """
        Load all statute documents
        
        Returns:
            DataFrame with case_id, text, and label columns
        """
        logger.info("Loading statutes...")
        
        statutes = []
        statute_files = [f for f in os.listdir(self.statutes_dir) if f.endswith('.txt')]
        
        for filename in statute_files:
            statute_id = filename.replace('.txt', '')
            filepath = os.path.join(self.statutes_dir, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                    title = ""
                    desc = ""
                    
                    for line in lines:
                        if line.startswith('Title:'):
                            title = line.replace('Title:', '').strip()
                        elif line.startswith('Desc:'):
                            desc = line.replace('Desc:', '').strip()
                    
                    # Combine title and description
                    text = f"{title}. {desc}".strip()
                    
                    if text:
                        statutes.append({
                            'case_id': statute_id,
                            'text': text,
                            'label': 'statute'
                        })
            except Exception as e:
                logger.warning(f"Error reading {filename}: {e}")
        
        logger.info(f"Loaded {len(statutes)} statutes")
        return pd.DataFrame(statutes)
    
    def load_queries(self) -> pd.DataFrame:
        """
        Load query documents
        
        Returns:
            DataFrame with case_id, text, and label columns
        """
        logger.info("Loading queries...")
        
        queries = []
        
        try:
            with open(self.query_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if '||' in line:
                        parts = line.strip().split('||', 1)
                        if len(parts) == 2:
                            query_id, query_text = parts
                            queries.append({
                                'case_id': query_id,
                                'text': query_text.strip(),
                                'label': 'query'
                            })
        except Exception as e:
            logger.error(f"Error reading queries: {e}")
        
        logger.info(f"Loaded {len(queries)} queries")
        return pd.DataFrame(queries)
    
    def convert_to_csv(self, output_dir: str = 'data/processed') -> str:
        """
        Convert entire AILA dataset to single CSV file
        
        Args:
            output_dir: Directory to save processed CSV
            
        Returns:
            Path to saved CSV file
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Load all components
        cases_df = self.load_case_documents()
        statutes_df = self.load_statutes()
        queries_df = self.load_queries()
        
        # Combine all documents
        all_docs = pd.concat([cases_df, statutes_df, queries_df], ignore_index=True)
        
        logger.info(f"Total documents: {len(all_docs)}")
        logger.info(f"  - Cases: {len(cases_df)}")
        logger.info(f"  - Statutes: {len(statutes_df)}")
        logger.info(f"  - Queries: {len(queries_df)}")
        
        # Save to CSV
        output_path = os.path.join(output_dir, 'aila_dataset.csv')
        all_docs.to_csv(output_path, index=False)
        logger.info(f"Saved dataset to {output_path}")
        
        return output_path


def main():
    """Main conversion function"""
    converter = AILADatasetConverter()
    output_path = converter.convert_to_csv()
    
    # Load and display sample
    df = pd.read_csv(output_path)
    print("\n=== Dataset Summary ===")
    print(f"Total records: {len(df)}")
    print(f"\nLabel distribution:")
    print(df['label'].value_counts())
    print(f"\nSample records:")
    print(df.head())
    print(f"\nAverage text length: {df['text'].str.len().mean():.0f} characters")


if __name__ == "__main__":
    main()
