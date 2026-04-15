# ⚖️ LexMind AI - Legal Intelligence System

> Deep Learning powered legal document retrieval, summarization, and conversational AI for Indian law

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![React](https://img.shields.io/badge/React-18+-61DAFB.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🎯 Overview

LexMind AI is a comprehensive legal intelligence platform that combines state-of-the-art NLP models with a beautiful React interface to provide:

- **🔍 Semantic Case Retrieval** - Find similar legal cases using MPNet embeddings and FAISS
- **📝 Document Summarization** - Generate concise summaries with BART
- **💬 RAG Chatbot** - Conversational AI powered by NVIDIA Nemotron with legal document context
- **📊 Analytics Dashboard** - Insights into your legal document corpus

## ✨ Features

### 1. Case Retrieval
- Semantic search through 3,111 legal documents (2,914 cases + 197 statutes)
- FAISS-powered vector similarity search
- MPNet embeddings (768 dimensions)
- Results in <100ms

### 2. Document Summarization
- BART-based abstractive summarization
- Adjustable summary length (min/max sliders)
- Searchable case selection (2,488 cases)
- Custom text summarization
- Compression ratio statistics

### 3. RAG Chatbot
- Conversational AI with legal context
- Retrieves relevant cases and statutes automatically
- Markdown-formatted responses with tables, lists, code blocks
- Chat history with beautiful UI
- Side-by-side document viewing
- Powered by NVIDIA Nemotron Nano 9B via OpenRouter

### 4. Analytics
- Document distribution by type
- Performance metrics
- Corpus statistics

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React + Tailwind)              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Retrieval│  │Summarize │  │   Chat   │  │Analytics │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (Flask + Python)                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  MPNet Embedder → FAISS Index → Retrieval Engine     │  │
│  │  BART Summarizer → Text Generation                   │  │
│  │  OpenRouter Client → NVIDIA Nemotron → RAG Pipeline  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data & Models                             │
│  • 2,914 case documents                                      │
│  • 197 statute documents                                     │
│  • FAISS index (768-dim vectors)                            │
│  • Pre-trained models (MPNet, BART, BERT)                   │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- 8GB RAM minimum
- OpenRouter API key (free tier available)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd "DL project"
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Frontend dependencies**
```bash
cd frontend
npm install
cd ..
```

4. **Set up environment variables**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your OpenRouter API key
# OPENROUTER_API_KEY=your_key_here
```

5. **Prepare the data** (if not already done)
```bash
# Run preprocessing notebook
jupyter notebook notebooks/preprocessing.ipynb

# Generate embeddings
jupyter notebook notebooks/embeddings_retrieval.ipynb
```

### Running the Application

**Terminal 1 - Backend:**
```bash
python backend_api.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access the app:**
Open http://localhost:3000 in your browser

## 📁 Project Structure

```
DL project/
├── backend_api.py              # Flask API server
├── src/
│   ├── embedder.py            # MPNet embedding generation
│   ├── retrieval.py           # FAISS retrieval engine
│   ├── summarizer.py          # BART summarization
│   └── qa_engine.py           # BERT Q&A (legacy)
├── data/
│   ├── raw/
│   │   ├── Object_casedocs/   # 2,914 case documents
│   │   └── Object_statutes/   # 197 statute documents
│   └── processed/
│       ├── train.csv          # Processed training data
│       └── test.csv           # Processed test data
├── models/
│   ├── embeddings/
│   │   ├── train_embeddings.index  # FAISS index
│   │   └── train_embeddings.npy    # Embedding vectors
│   ├── summarizer/            # BART model cache
│   └── bert_qa/               # BERT model cache
├── frontend/
│   ├── src/
│   │   ├── App.tsx            # Main React application
│   │   ├── index.css          # Tailwind styles
│   │   └── main.tsx           # Entry point
│   ├── package.json
│   └── vite.config.ts
├── notebooks/
│   ├── preprocessing.ipynb    # Data preprocessing
│   └── embeddings_retrieval.ipynb  # Embedding generation
├── .env                       # Environment variables (create this)
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
# OpenRouter API Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# CORS Configuration
FRONTEND_URL=http://localhost:3000
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/retrieve` | POST | Semantic case retrieval |
| `/api/summarize` | POST | Document summarization |
| `/api/chat` | POST | RAG chatbot |
| `/api/qa` | POST | Q&A (legacy) |
| `/api/stats` | GET | Analytics data |
| `/api/cases` | GET | List all cases |
| `/api/case/<id>` | GET | Get specific case |

## 🎨 UI Features

### Chat Interface
- **Markdown rendering** - Bold, italics, tables, code blocks, lists
- **Side-by-side layout** - Chat (60%) + Documents (40%)
- **Auto-scroll** - Always shows latest messages
- **Expandable documents** - Click to view full text
- **Clear chat** - Start fresh conversations
- **Loading indicators** - Smooth animations

### Summarization
- **Searchable dropdown** - Type to filter 2,488 cases
- **Adjustable length** - Min/max sliders
- **Custom text** - Paste any document
- **Statistics** - Compression ratio, character counts
- **View original** - Expandable full document

### Retrieval
- **Fast search** - Results in <100ms
- **Similarity scores** - Percentage match
- **Document preview** - Expandable full text
- **Mixed results** - Cases + Statutes

## 🤖 AI Models

| Model | Purpose | Size | Speed |
|-------|---------|------|-------|
| **MPNet** | Embeddings | 420MB | <100ms |
| **FAISS** | Vector search | 7.5MB | <50ms |
| **BART** | Summarization | 1.6GB | 30-60s |
| **BERT** | Q&A (legacy) | 440MB | 1-2s |
| **Nemotron 9B** | Chat (via API) | N/A | 2-5s |

## 📊 Dataset

**AILA 2019 Dataset** - Artificial Intelligence for Legal Assistance

- **Total Documents:** 3,111
  - Prior Cases: 2,914
  - Statutes: 197
- **Domain:** Indian Law
- **Format:** Plain text
- **Preprocessing:** Cleaned, tokenized, embedded

## 🚢 Deployment

### ⚠️ Important: Vercel Limitations

Vercel's free tier **cannot** host this application due to:
- 10-second function timeout (models take 20-30s to load)
- 250MB deployment size limit (models are larger)
- 1GB memory limit (insufficient for models)

### ✅ Recommended: Railway + Vercel

**Backend on Railway** (supports large apps):
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up

# Set environment variable
railway variables set OPENROUTER_API_KEY=your_key_here

# Get your URL
railway domain
```

**Frontend on Vercel**:
```bash
# Update API URLs in frontend/src/App.tsx
# Replace http://localhost:5000 with your Railway URL

cd frontend
npm run build
vercel --prod
```

### Alternative Platforms

| Platform | Free Tier | Suitable | Notes |
|----------|-----------|----------|-------|
| **Railway** | 500 hrs/month | ✅ Yes | Best for backend |
| **Render** | 750 hrs/month | ✅ Yes | Good alternative |
| **Fly.io** | 3 VMs free | ✅ Yes | More complex |
| **Vercel** | Unlimited | ❌ No | Frontend only |
| **Heroku** | Deprecated | ❌ No | No longer free |

## 🔒 Security

- **API Keys**: Never commit `.env` file
- **CORS**: Configured for specific origins
- **Input Validation**: All endpoints validate input
- **Rate Limiting**: Consider adding for production
- **HTTPS**: Use in production

## 🧪 Testing

### Manual Testing

1. **Retrieval**: Search for "cheque dishonour"
2. **Summarization**: Select case C1, adjust sliders
3. **Chat**: Ask "What is the punishment for theft?"
4. **Analytics**: View document distribution

### Expected Results

- Retrieval: 5 results in <100ms
- Summarization: 30-60 seconds
- Chat: 2-5 seconds per response
- All features: No errors

## 📈 Performance

- **Retrieval**: <100ms (FAISS)
- **Summarization**: 30-60s (BART on CPU)
- **Chat**: 2-5s (OpenRouter API)
- **Memory**: ~4GB (all models loaded)
- **Disk**: ~3GB (models + data)

## 🛠️ Development

### Adding New Features

1. **Backend**: Add endpoint in `backend_api.py`
2. **Frontend**: Add UI in `frontend/src/App.tsx`
3. **Models**: Add in `src/` directory
4. **Test**: Manual testing + validation

### Code Style

- **Python**: PEP 8
- **TypeScript**: ESLint + Prettier
- **React**: Functional components + hooks
- **CSS**: Tailwind utility classes

## 🐛 Troubleshooting

### Backend Issues

**Models not loading:**
```bash
# Check if files exist
ls models/embeddings/
ls data/processed/

# Re-run preprocessing if needed
jupyter notebook notebooks/preprocessing.ipynb
```

**CORS errors:**
```python
# Update CORS in backend_api.py
CORS(app, origins=['http://localhost:3000', 'your-frontend-url'])
```

**OpenRouter errors:**
```bash
# Check API key
echo $OPENROUTER_API_KEY

# Test API
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

### Frontend Issues

**Blank screen:**
```bash
# Check console for errors
# Rebuild
cd frontend
rm -rf node_modules dist
npm install
npm run dev
```

**API connection failed:**
```typescript
// Check API URL in App.tsx
// Should match backend URL
fetch('http://localhost:5000/api/...')
```

## 📚 Resources

- **AILA Dataset**: [Competition Page](https://sites.google.com/view/fire-2019-aila/)
- **MPNet**: [Sentence Transformers](https://www.sbert.net/)
- **FAISS**: [Facebook AI](https://github.com/facebookresearch/faiss)
- **BART**: [Hugging Face](https://huggingface.co/facebook/bart-large-cnn)
- **OpenRouter**: [Documentation](https://openrouter.ai/docs)
- **Railway**: [Deployment Guide](https://docs.railway.app/)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- AILA 2019 organizers for the dataset
- Hugging Face for pre-trained models
- OpenRouter for LLM API access
- React and Tailwind communities

## 📞 Support

- **Issues**: Open a GitHub issue
- **Email**: your.email@example.com
- **Documentation**: See this README

---

**Built with ❤️ using Python, React, and Deep Learning**

⭐ Star this repo if you find it useful!
