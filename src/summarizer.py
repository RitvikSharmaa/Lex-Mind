"""
Legal Document Summarizer using BART
Implements abstractive summarization for legal judgments
"""

import logging
from typing import List, Union
import pandas as pd
from transformers import BartForConditionalGeneration, BartTokenizer
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LegalSummarizer:
    """
    Abstractive summarization using BART model
    Model: facebook/bart-large-cnn
    """
    
    def __init__(self, model_name: str = "facebook/bart-large-cnn"):
        """
        Initialize BART summarizer
        
        Args:
            model_name: HuggingFace model identifier
        """
        self.model_name = model_name
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
        logger.info(f"Loading summarization model: {model_name}")
        self.tokenizer = BartTokenizer.from_pretrained(model_name)
        self.model = BartForConditionalGeneration.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()
        logger.info("Model loaded successfully")
    
    def summarize(
        self,
        text: str,
        max_length: int = 150,
        min_length: int = 50,
        num_beams: int = 4,
        length_penalty: float = 2.0,
        early_stopping: bool = True
    ) -> str:
        """
        Generate summary for a single text
        
        Args:
            text: Input legal document text
            max_length: Maximum summary length in tokens
            min_length: Minimum summary length in tokens
            num_beams: Beam search width
            length_penalty: Length penalty for beam search
            early_stopping: Stop when all beams finish
            
        Returns:
            Generated summary text
        """
        # Tokenize input
        inputs = self.tokenizer(
            text,
            max_length=1024,
            truncation=True,
            return_tensors="pt"
        ).to(self.device)
        
        # Generate summary
        with torch.no_grad():
            summary_ids = self.model.generate(
                inputs["input_ids"],
                max_length=max_length,
                min_length=min_length,
                num_beams=num_beams,
                length_penalty=length_penalty,
                early_stopping=early_stopping
            )
        
        # Decode summary
        summary = self.tokenizer.decode(
            summary_ids[0],
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True
        )
        
        return summary
    
    def summarize_batch(
        self,
        texts: List[str],
        max_length: int = 150,
        min_length: int = 50,
        batch_size: int = 8
    ) -> List[str]:
        """
        Generate summaries for multiple texts
        
        Args:
            texts: List of input texts
            max_length: Maximum summary length
            min_length: Minimum summary length
            batch_size: Number of texts to process at once
            
        Returns:
            List of generated summaries
        """
        summaries = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            
            # Tokenize batch
            inputs = self.tokenizer(
                batch_texts,
                max_length=1024,
                truncation=True,
                padding=True,
                return_tensors="pt"
            ).to(self.device)
            
            # Generate summaries
            with torch.no_grad():
                summary_ids = self.model.generate(
                    inputs["input_ids"],
                    max_length=max_length,
                    min_length=min_length,
                    num_beams=4,
                    length_penalty=2.0,
                    early_stopping=True
                )
            
            # Decode summaries
            batch_summaries = self.tokenizer.batch_decode(
                summary_ids,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True
            )
            
            summaries.extend(batch_summaries)
            logger.info(f"Processed {len(summaries)}/{len(texts)} documents")
        
        return summaries
    
    def summarize_dataframe(
        self,
        df: pd.DataFrame,
        text_column: str = 'text',
        max_length: int = 150,
        min_length: int = 50,
        batch_size: int = 8
    ) -> pd.DataFrame:
        """
        Add summaries to a dataframe
        
        Args:
            df: Input dataframe with text column
            text_column: Name of column containing text
            max_length: Maximum summary length
            min_length: Minimum summary length
            batch_size: Batch size for processing
            
        Returns:
            Dataframe with added 'summary' column
        """
        logger.info(f"Summarizing {len(df)} documents...")
        
        texts = df[text_column].tolist()
        summaries = self.summarize_batch(
            texts,
            max_length=max_length,
            min_length=min_length,
            batch_size=batch_size
        )
        
        df_copy = df.copy()
        df_copy['summary'] = summaries
        
        logger.info("Summarization complete")
        return df_copy


def summarize_and_save(
    input_path: str,
    output_path: str,
    text_column: str = 'text',
    max_length: int = 150,
    min_length: int = 50,
    batch_size: int = 8
) -> pd.DataFrame:
    """
    Load data, generate summaries, and save results
    
    Args:
        input_path: Path to input CSV file
        output_path: Path to save output CSV
        text_column: Name of text column
        max_length: Maximum summary length
        min_length: Minimum summary length
        batch_size: Batch size for processing
        
    Returns:
        Dataframe with summaries
    """
    # Load data
    logger.info(f"Loading data from {input_path}")
    df = pd.read_csv(input_path)
    logger.info(f"Loaded {len(df)} records")
    
    # Initialize summarizer
    summarizer = LegalSummarizer()
    
    # Generate summaries
    df_with_summaries = summarizer.summarize_dataframe(
        df,
        text_column=text_column,
        max_length=max_length,
        min_length=min_length,
        batch_size=batch_size
    )
    
    # Save results
    df_with_summaries.to_csv(output_path, index=False)
    logger.info(f"Saved summaries to {output_path}")
    
    return df_with_summaries


if __name__ == "__main__":
    # Test with sample data
    sample_text = """
    The appellant filed a petition under Section 138 of the Negotiable Instruments Act
    alleging that the respondent issued a cheque which was dishonored due to insufficient
    funds. The trial court convicted the respondent and imposed a fine. The respondent
    appealed to the High Court challenging the conviction. The High Court upheld the
    conviction but reduced the sentence. The appellant is now challenging the reduction
    in sentence before this Court.
    """
    
    summarizer = LegalSummarizer()
    summary = summarizer.summarize(sample_text)
    
    print("Original Text:")
    print(sample_text)
    print("\nGenerated Summary:")
    print(summary)
