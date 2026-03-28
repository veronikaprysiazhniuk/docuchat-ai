# 🤖 DocuChat AI — Chat With Your Documents

> AI-powered chatbot that answers questions from uploaded business documents using RAG (Retrieval-Augmented Generation).

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40-red)
![Claude](https://img.shields.io/badge/Claude_API-Supported-green)

## Features

- **📄 Document Upload** — PDF, TXT, Markdown files
- **🔍 RAG Architecture** — Retrieves relevant context before answering
- **🌍 Multilingual** — Responds in English, French, German
- **📎 Source Citations** — Every answer shows which document section it came from
- **🎯 Demo Mode** — Works without API key (built-in sample data)
- **🔑 Production Mode** — Connect Claude API for real AI-powered answers

## Use Cases

| Client Type | Problem | Solution |
|------------|---------|----------|
| Restaurant | Staff answering same menu questions | Chatbot handles 80% of FAQs automatically |
| Law Firm | Clients asking about procedures | Bot answers from uploaded legal docs |
| E-commerce | Product questions at 2am | 24/7 AI support from product catalog |
| Real Estate | Property inquiries | Bot qualifies leads + answers from listings |
| Clinic | Patient appointment/procedure FAQs | Reduces receptionist workload by 60% |

## Quick Start

```bash
# Clone
git clone https://github.com/veronikaprysiazhniuk/docuchat-ai.git
cd docuchat-ai

# Install
pip install -r requirements.txt

# Run (demo mode - no API key needed)
streamlit run app.py

# Production mode - set your Claude API key in the sidebar
```

## Architecture

```
User Question
    ↓
[Text Chunking] → Document split into overlapping chunks
    ↓
[Retrieval] → Find most relevant chunks (keyword/semantic search)
    ↓
[Context Assembly] → Top 3 chunks + user question
    ↓
[Claude API / Demo Engine] → Generate contextual answer
    ↓
Response + Source Citations
```

## Deploy Free

### Streamlit Cloud
1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repo → Deploy
4. Add Claude API key in Streamlit secrets (optional)

## Tech Stack

- **Streamlit** — Web interface & deployment
- **Claude API** — AI response generation (production mode)
- **PyPDF2** — PDF text extraction
- **Custom RAG** — Text chunking + keyword retrieval

## Scaling to Production

For production deployment with real clients, upgrade to:
- **ChromaDB / FAISS** for vector-based semantic search
- **LangChain** for advanced RAG pipelines
- **Supabase** for persistent document storage
- **Vercel / Railway** for always-on hosting

## Author

**Veronika Prysiazhniuk** — AI Automation & Chatbot Specialist

- Physics background with ML research experience (neural networks, embeddings, latent space analysis)
- Based in Luxembourg — multilingual support (EN/FR/DE)
- Available for freelance: https://www.upwork.com/freelancers/~01d67eff79a13e80dc?mp_source=share

## License

MIT License
