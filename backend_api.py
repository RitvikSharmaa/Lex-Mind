"""
Flask API Backend for LexMind AI React Frontend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
from dotenv import load_dotenv
from src.embedder import LegalEmbedder
from src.retrieval import FAISSRetriever
from src.summarizer import LegalSummarizer
from src.qa_engine import LegalQAEngine
from openai import OpenAI

# Load environment variables
load_dotenv()

app = Flask(__name__)

# CORS configuration
frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
CORS(app, origins=[frontend_url, 'http://localhost:3000', 'http://localhost:5173'])

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable is not set")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# Initialize models (load once at startup)
print("Loading models...")
embedder = LegalEmbedder()
retriever = FAISSRetriever(embedding_dim=768)
retriever.load_index('models/embeddings/train_embeddings.index')
train_df = pd.read_csv('data/processed/train.csv')
retriever.set_documents(train_df)
summarizer = LegalSummarizer()
qa_engine = LegalQAEngine()
print("Models loaded successfully!")

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "models_loaded": True})

@app.route('/api/retrieve', methods=['POST'])
def retrieve():
    data = request.json
    query = data.get('query', '')
    k = data.get('k', 5)
    
    # Encode query
    query_embedding = embedder.encode_texts([query])[0]
    
    # Retrieve similar documents
    results = retriever.retrieve(query_embedding, k=k)
    
    # Convert to list of dicts
    results_list = results.to_dict('records')
    
    return jsonify({
        "results": results_list,
        "count": len(results_list)
    })

@app.route('/api/summarize', methods=['POST'])
def summarize():
    data = request.json
    text = data.get('text', '')
    max_length = data.get('max_length', 150)
    min_length = data.get('min_length', 50)
    
    print(f"Summarization request: max_length={max_length}, min_length={min_length}")
    print(f"Original text length: {len(text)}")
    
    # Truncate if too long (increased to 5000 for better summaries)
    text_to_summarize = text[:5000] if len(text) > 5000 else text
    print(f"Text to summarize length: {len(text_to_summarize)}")
    
    # Generate summary
    summary = summarizer.summarize(
        text_to_summarize,
        max_length=max_length,
        min_length=min_length
    )
    
    print(f"Generated summary length: {len(summary)}")
    
    return jsonify({
        "summary": summary,
        "original_length": len(text),
        "summary_length": len(summary),
        "compression_ratio": (len(summary) / len(text)) * 100
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """RAG-based chat using OpenRouter LLM"""
    data = request.json
    question = data.get('question', '')
    chat_history = data.get('history', [])
    
    # Check if question needs retrieval (skip for greetings/small talk)
    greeting_keywords = ['hi', 'hello', 'hey', 'thanks', 'thank you', 'bye', 'goodbye']
    needs_retrieval = not any(keyword == question.lower().strip() for keyword in greeting_keywords)
    
    retrieved_docs = None
    context = ""
    
    if needs_retrieval:
        # Step 1: Retrieve relevant documents
        query_embedding = embedder.encode_texts([question])[0]
        all_retrieved = retriever.retrieve(query_embedding, k=10)  # Get more results
        
        # Step 2: Separate cases and statutes
        cases = all_retrieved[all_retrieved['label'] == 'prior_case'].head(2)
        statutes = all_retrieved[all_retrieved['label'] == 'statute'].head(2)
        
        # Combine: prioritize getting at least 1 of each type if available
        retrieved_docs_list = []
        if len(cases) > 0:
            retrieved_docs_list.append(cases.iloc[0])
        if len(statutes) > 0:
            retrieved_docs_list.append(statutes.iloc[0])
        if len(cases) > 1:
            retrieved_docs_list.append(cases.iloc[1])
        if len(statutes) > 1:
            retrieved_docs_list.append(statutes.iloc[1])
            
        # Convert back to DataFrame
        if retrieved_docs_list:
            retrieved_docs = pd.DataFrame(retrieved_docs_list)
        else:
            retrieved_docs = all_retrieved.head(3)  # Fallback to top 3
        
        # Step 3: Prepare context from retrieved documents
        context = "\n\n".join([
            f"Document {i+1} ({row['case_id']}) - {row['label'].upper()}:\n{row['text'][:2000]}"  # Increased to 2000 chars
            for i, (_, row) in enumerate(retrieved_docs.iterrows())
        ])
    
    # Step 3: Build messages for LLM
    if needs_retrieval and context:
        system_message = f"""You are a legal AI assistant specializing in Indian law. Answer questions based on the provided legal documents.

Retrieved Legal Documents:
{context}

Instructions:
- Provide clear, accurate answers based on the documents
- Cite specific case IDs when referencing information
- Use **bold** for important terms and case names
- Use *italics* for legal terminology
- Use bullet points (-) for lists
- Use numbered lists (1., 2., 3.) for steps or procedures
- Use tables when comparing multiple cases or sections
- Keep answers concise but informative
- Format your response in markdown for better readability"""
    else:
        system_message = """You are a legal AI assistant specializing in Indian law. You can answer questions about Indian law, legal procedures, and provide general legal information. Be helpful and friendly.

Instructions:
- Use **bold** for important terms
- Use *italics* for emphasis
- Use bullet points for lists
- Format your response in markdown for better readability"""
    
    messages = [{"role": "system", "content": system_message}]
    
    # Add chat history
    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Add current question
    messages.append({"role": "user", "content": question})
    
    # Step 4: Get response from OpenRouter (using free model)
    try:
        completion = client.chat.completions.create(
            model="nvidia/nemotron-nano-9b-v2:free",  # Fast free model
            messages=messages,
            max_tokens=1500,  # Increased for longer responses
            temperature=0.7,
        )
        
        answer = completion.choices[0].message.content
        
        # Prepare response
        response_data = {
            "answer": answer,
            "success": True
        }
        
        # Only include retrieved docs if we actually retrieved them
        if needs_retrieval and retrieved_docs is not None:
            response_data["retrieved_docs"] = retrieved_docs[['case_id', 'label', 'similarity_score', 'text']].to_dict('records')
        else:
            response_data["retrieved_docs"] = []
        
        return jsonify(response_data)
    except Exception as e:
        print(f"OpenRouter error: {e}")
        return jsonify({
            "answer": f"Error: {str(e)}",
            "retrieved_docs": [],
            "success": False
        }), 500

@app.route('/api/qa', methods=['POST'])
def qa():
    data = request.json
    question = data.get('question', '')
    top_k = data.get('top_k', 5)
    
    # Get answer with retrieval
    result = qa_engine.answer_with_retrieval(
        question=question,
        retriever=retriever,
        embedder=embedder,
        top_k=top_k
    )
    
    # Convert dataframe to dict
    result['retrieved_documents'] = result['retrieved_documents'].to_dict('records')
    
    # Convert numpy types to Python types for JSON serialization
    result['confidence'] = float(result['confidence'])
    for answer in result['all_answers']:
        answer['confidence'] = float(answer['confidence'])
        answer['similarity_score'] = float(answer['similarity_score'])
    
    return jsonify(result)

@app.route('/api/stats', methods=['GET'])
def stats():
    return jsonify({
        "total_documents": len(train_df),
        "embedding_dim": 768,
        "labels": train_df['label'].value_counts().to_dict(),
        "avg_length": int(train_df['text_length'].mean()),
        "max_length": int(train_df['text_length'].max()),
        "min_length": int(train_df['text_length'].min())
    })

@app.route('/api/cases', methods=['GET'])
def get_cases():
    # Return ALL cases from the training set
    cases = train_df['case_id'].tolist()
    return jsonify({"cases": cases, "total": len(cases)})

@app.route('/api/case/<case_id>', methods=['GET'])
def get_case(case_id):
    case = train_df[train_df['case_id'] == case_id]
    if len(case) == 0:
        return jsonify({"error": "Case not found"}), 404
    
    return jsonify(case.iloc[0].to_dict())

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
