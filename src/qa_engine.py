"""
Legal Question Answering Engine using BERT
Implements extractive QA for legal queries
"""

import logging
from typing import List, Dict, Tuple
import pandas as pd
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LegalQAEngine:
    """
    Question Answering using BERT
    Model: nlpaueb/legal-bert-base-uncased (or bert-base-uncased as fallback)
    """
    
    def __init__(self, model_name: str = "bert-base-uncased"):
        """
        Initialize QA engine
        
        Args:
            model_name: HuggingFace model identifier
        """
        self.model_name = model_name
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
        logger.info(f"Loading QA model: {model_name}")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForQuestionAnswering.from_pretrained(model_name)
        except Exception as e:
            logger.warning(f"Failed to load {model_name}, using bert-base-uncased: {e}")
            self.model_name = "bert-base-uncased"
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForQuestionAnswering.from_pretrained(self.model_name)
        
        self.model.to(self.device)
        self.model.eval()
        logger.info("Model loaded successfully")
    
    def answer_question(
        self,
        question: str,
        context: str,
        max_answer_length: int = 100
    ) -> Dict[str, any]:
        """
        Answer a question based on context
        
        Args:
            question: Question text
            context: Context text to extract answer from
            max_answer_length: Maximum length of answer
            
        Returns:
            Dictionary with answer, score, start, and end positions
        """
        # Truncate context if too long
        if len(context) > 2000:
            context = context[:2000]
        
        # Tokenize inputs
        inputs = self.tokenizer(
            question,
            context,
            max_length=512,
            truncation=True,
            return_tensors="pt"
        ).to(self.device)
        
        # Get model predictions
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Get answer span
        answer_start = torch.argmax(outputs.start_logits)
        answer_end = torch.argmax(outputs.end_logits)
        
        # Ensure valid span
        if answer_end < answer_start:
            answer_end = answer_start + 10  # Default to small span
        
        # Limit answer length
        if answer_end - answer_start > max_answer_length:
            answer_end = answer_start + max_answer_length
        
        # Extract answer
        answer_tokens = inputs["input_ids"][0][answer_start:answer_end + 1]
        answer = self.tokenizer.decode(answer_tokens, skip_special_tokens=True)
        
        # Clean up answer
        answer = answer.strip()
        
        # If answer is too short, expand to include more context
        if len(answer) < 50 and answer_end - answer_start < 20:
            # Expand the span to include more tokens
            expanded_start = max(0, answer_start - 30)
            expanded_end = min(len(inputs["input_ids"][0]), answer_end + 30)
            expanded_tokens = inputs["input_ids"][0][expanded_start:expanded_end]
            answer = self.tokenizer.decode(expanded_tokens, skip_special_tokens=True).strip()
        
        # Calculate confidence score
        start_score = torch.max(outputs.start_logits).item()
        end_score = torch.max(outputs.end_logits).item()
        confidence = (start_score + end_score) / 2
        
        return {
            "answer": answer,
            "confidence": confidence,
            "start": answer_start.item(),
            "end": answer_end.item()
        }
    
    def answer_from_multiple_contexts(
        self,
        question: str,
        contexts: List[str],
        top_k: int = 3
    ) -> List[Dict[str, any]]:
        """
        Answer question using multiple context documents
        
        Args:
            question: Question text
            contexts: List of context texts
            top_k: Number of top answers to return
            
        Returns:
            List of answer dictionaries sorted by confidence
        """
        answers = []
        
        for idx, context in enumerate(contexts):
            result = self.answer_question(question, context)
            result['context_index'] = idx
            result['context_preview'] = context[:200] + "..."
            answers.append(result)
        
        # Sort by confidence
        answers.sort(key=lambda x: x['confidence'], reverse=True)
        
        return answers[:top_k]
    
    def answer_with_retrieval(
        self,
        question: str,
        retriever,
        embedder,
        top_k: int = 5
    ) -> Dict[str, any]:
        """
        Answer question using retrieval + QA pipeline
        
        Args:
            question: Question text
            retriever: FAISSRetriever instance
            embedder: LegalEmbedder instance
            top_k: Number of documents to retrieve
            
        Returns:
            Dictionary with answer and supporting documents
        """
        # Encode question
        question_embedding = embedder.encode_texts([question])[0]
        
        # Retrieve relevant documents
        retrieved_docs = retriever.retrieve(question_embedding, k=top_k)
        
        # Get contexts
        contexts = retrieved_docs['text'].tolist()
        
        # Answer from multiple contexts
        answers = self.answer_from_multiple_contexts(question, contexts, top_k=3)
        
        # Add document metadata
        for i, answer in enumerate(answers):
            ctx_idx = answer['context_index']
            answer['case_id'] = retrieved_docs.iloc[ctx_idx]['case_id']
            answer['label'] = retrieved_docs.iloc[ctx_idx].get('label', 'N/A')
            answer['similarity_score'] = retrieved_docs.iloc[ctx_idx]['similarity_score']
        
        return {
            "question": question,
            "best_answer": answers[0]['answer'],
            "confidence": answers[0]['confidence'],
            "all_answers": answers,
            "retrieved_documents": retrieved_docs
        }


def test_qa_engine():
    """Test QA engine with sample data"""
    
    # Sample legal context
    context = """
    Section 138 of the Negotiable Instruments Act deals with dishonour of cheque for 
    insufficiency of funds. When a cheque is returned by the bank unpaid, either because 
    the amount of money standing to the credit of that account is insufficient to honour 
    the cheque or that it exceeds the amount arranged to be paid from that account, the 
    drawer of such cheque shall be deemed to have committed an offence. The punishment 
    for this offence is imprisonment for a term which may extend to two years, or with 
    fine which may extend to twice the amount of the cheque, or with both.
    """
    
    # Sample questions
    questions = [
        "What is Section 138 about?",
        "What is the punishment for cheque dishonour?",
        "What happens when a cheque is returned unpaid?"
    ]
    
    # Initialize QA engine
    qa_engine = LegalQAEngine()
    
    print("="*60)
    print("Legal QA Engine Test")
    print("="*60)
    print(f"\nContext:\n{context}\n")
    
    for question in questions:
        result = qa_engine.answer_question(question, context)
        print(f"\nQuestion: {question}")
        print(f"Answer: {result['answer']}")
        print(f"Confidence: {result['confidence']:.4f}")
        print("-" * 60)


if __name__ == "__main__":
    test_qa_engine()
