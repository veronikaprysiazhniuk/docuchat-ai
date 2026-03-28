"""
🤖 DocuChat AI — Chat With Your Documents
AI-powered chatbot that answers questions from uploaded business documents.

Portfolio Demo by Veronika Prysiazhniuk
- Upload PDFs, TXT files
- Ask questions in natural language
- Supports multiple languages (EN/FR/DE)
- RAG architecture with vector search

Deploy: streamlit run app.py
"""

import streamlit as st
import hashlib
import json
import re
from datetime import datetime

# ─── Page Config ───
st.set_page_config(
    page_title="DocuChat AI",
    page_icon="🤖",
    layout="wide"
)

# ─── Custom CSS ───
st.markdown("""
<style>
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00b894 0%, #00cec9 50%, #0984e3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .subtitle {
        color: #636e72;
        font-size: 1rem;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    .chat-user {
        background: #dfe6e9;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        margin-left: 20%;
        font-size: 0.95rem;
    }
    .chat-bot {
        background: linear-gradient(135deg, #e8f5e9 0%, #e3f2fd 100%);
        padding: 12px 18px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        margin-right: 20%;
        font-size: 0.95rem;
        border-left: 3px solid #00b894;
    }
    .doc-badge {
        display: inline-block;
        background: #00b894;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 4px;
    }
    .feature-card {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 20px;
        margin: 8px 0;
    }
    .source-ref {
        background: #fff3e0;
        border-left: 3px solid #ff9800;
        padding: 8px 14px;
        border-radius: 0 8px 8px 0;
        font-size: 0.85rem;
        color: #e65100;
        margin-top: 8px;
    }
    .lang-selector {
        display: flex;
        gap: 8px;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Initialize Session State ───
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'documents' not in st.session_state:
    st.session_state.documents = {}
if 'api_mode' not in st.session_state:
    st.session_state.api_mode = 'demo'

# ─── Simulated Knowledge Base (for demo without API key) ───
DEMO_KNOWLEDGE = {
    "restaurant_menu": {
        "name": "La Belle Cuisine — Restaurant Menu & FAQ",
        "content": """
        La Belle Cuisine is a French-Italian fusion restaurant in Luxembourg City.
        
        STARTERS:
        - French Onion Soup - €8.50 (vegetarian, gluten-free option available)
        - Bruschetta Trio - €9.00 (vegetarian)
        - Carpaccio di Manzo - €12.00
        - Caesar Salad - €10.50 (can be made without croutons for GF)
        
        MAIN COURSES:
        - Filet Mignon with truffle sauce - €28.00
        - Pan-seared Sea Bass - €24.00
        - Risotto ai Funghi Porcini - €18.00 (vegetarian)
        - Duck Confit with cherry reduction - €22.00
        - Pasta Carbonara (house-made) - €16.00
        - Grilled Vegetable Platter - €15.00 (vegan, gluten-free)
        
        DESSERTS:
        - Crème Brûlée - €7.50
        - Tiramisu - €8.00
        - Chocolate Fondant - €9.00
        - Seasonal Fruit Sorbet - €6.50 (vegan)
        
        DRINKS:
        - House Wine (glass) - €6.00
        - Craft Cocktails - €12.00-€14.00
        - Non-alcoholic Mocktails - €8.00
        
        OPENING HOURS:
        Monday-Friday: 12:00-14:30, 18:30-22:00
        Saturday: 18:30-23:00
        Sunday: Closed
        
        ALLERGIES: All dishes can be modified for common allergies. Please inform your server.
        RESERVATIONS: Required for groups of 6+. Call +352 XX XXX XXX or book online.
        PARKING: Free parking available behind the building (20 spots).
        PRIVATE EVENTS: We host private events for up to 40 guests. Contact events@labellecuisine.lu
        """,
        "language_responses": {
            "en": "English response",
            "fr": "Réponse en français",
            "de": "Antwort auf Deutsch"
        }
    }
}

def chunk_text(text, chunk_size=300, overlap=50):
    """Split text into overlapping chunks for retrieval"""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk.strip())
    return chunks

def simple_search(query, chunks, top_k=3):
    """Simple keyword-based search (simulates vector search for demo)"""
    query_words = set(query.lower().split())
    scores = []
    
    for i, chunk in enumerate(chunks):
        chunk_lower = chunk.lower()
        # Score based on keyword overlap
        score = sum(1 for word in query_words if word in chunk_lower)
        # Bonus for exact phrase matches
        if query.lower() in chunk_lower:
            score += 5
        # Bonus for relevant keywords
        for word in query_words:
            score += chunk_lower.count(word) * 0.5
        scores.append((score, i, chunk))
    
    scores.sort(reverse=True, key=lambda x: x[0])
    return [(s[2], s[0]) for s in scores[:top_k] if s[0] > 0]

def generate_demo_response(query, relevant_chunks, language="en"):
    """Generate a contextual response from retrieved chunks (demo mode - no API needed)"""
    query_lower = query.lower()
    context = "\n".join([chunk for chunk, score in relevant_chunks])
    
    if not relevant_chunks:
        responses = {
            "en": "I couldn't find specific information about that in the uploaded documents. Could you rephrase your question or ask about something else?",
            "fr": "Je n'ai pas trouvé d'information spécifique à ce sujet dans les documents. Pourriez-vous reformuler votre question ?",
            "de": "Ich konnte keine spezifischen Informationen dazu in den Dokumenten finden. Können Sie Ihre Frage umformulieren?"
        }
        return responses.get(language, responses["en"]), []
    
    # Build response based on context
    sources = []
    response_parts = []
    
    # Extract relevant information
    for chunk, score in relevant_chunks:
        if score > 0:
            sources.append(chunk[:100] + "...")
    
    # Smart response generation based on query type
    if any(word in query_lower for word in ['vegetarian', 'vegan', 'végétarien', 'vegetarisch']):
        items = []
        for chunk, _ in relevant_chunks:
            lines = chunk.split('\n')
            for line in lines:
                if 'vegetarian' in line.lower() or 'vegan' in line.lower():
                    items.append(line.strip().lstrip('- '))
        
        if items:
            if language == "fr":
                response_parts.append(f"Voici les options végétariennes/véganes disponibles :\n")
            elif language == "de":
                response_parts.append(f"Hier sind die vegetarischen/veganen Optionen:\n")
            else:
                response_parts.append(f"Here are the vegetarian/vegan options I found:\n")
            for item in items:
                response_parts.append(f"• {item}")
    
    elif any(word in query_lower for word in ['price', 'cost', 'how much', 'prix', 'combien', 'preis', 'kosten']):
        items = []
        for chunk, _ in relevant_chunks:
            lines = chunk.split('\n')
            for line in lines:
                if '€' in line or '$' in line:
                    items.append(line.strip().lstrip('- '))
        
        if items:
            if language == "fr":
                response_parts.append("Voici les informations de prix que j'ai trouvées :\n")
            elif language == "de":
                response_parts.append("Hier sind die Preisinformationen:\n")
            else:
                response_parts.append("Here are the pricing details I found:\n")
            for item in items[:8]:
                response_parts.append(f"• {item}")
    
    elif any(word in query_lower for word in ['hour', 'open', 'when', 'heure', 'ouvert', 'quand', 'öffnungszeiten', 'wann']):
        for chunk, _ in relevant_chunks:
            lines = chunk.split('\n')
            for line in lines:
                line_lower = line.lower()
                if any(day in line_lower for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'lundi', 'mardi', 'montag']):
                    response_parts.append(line.strip())
                elif 'closed' in line_lower or 'fermé' in line_lower or 'geschlossen' in line_lower:
                    response_parts.append(line.strip())
        
        if not response_parts:
            response_parts.append(context[:300])
    
    elif any(word in query_lower for word in ['allergy', 'allergies', 'gluten', 'allergie', 'allergien']):
        for chunk, _ in relevant_chunks:
            if 'allerg' in chunk.lower() or 'gluten' in chunk.lower():
                response_parts.append(chunk.strip())
    
    elif any(word in query_lower for word in ['book', 'reservation', 'réserv', 'reserv', 'buchung']):
        for chunk, _ in relevant_chunks:
            if 'reserv' in chunk.lower() or 'book' in chunk.lower() or 'buchung' in chunk.lower():
                lines = chunk.split('\n')
                for line in lines:
                    if any(word in line.lower() for word in ['reserv', 'book', 'call', 'contact', 'group']):
                        response_parts.append(line.strip())
    
    else:
        # General query - return most relevant context
        if language == "fr":
            response_parts.append("D'après les documents, voici ce que j'ai trouvé :\n")
        elif language == "de":
            response_parts.append("Laut den Dokumenten habe ich Folgendes gefunden:\n")
        else:
            response_parts.append("Based on the documents, here's what I found:\n")
        
        for chunk, _ in relevant_chunks[:2]:
            clean_chunk = '\n'.join([line.strip() for line in chunk.split('\n') if line.strip()])
            response_parts.append(clean_chunk[:400])
    
    if not response_parts:
        response_parts.append(f"Based on the available information:\n{context[:300]}")
    
    response = '\n'.join(response_parts)
    return response, sources

def generate_api_response(query, relevant_chunks, api_key, language="en"):
    """Generate response using Claude API (production mode)"""
    try:
        import anthropic
        
        client = anthropic.Anthropic(api_key=api_key)
        
        context = "\n---\n".join([chunk for chunk, score in relevant_chunks])
        
        lang_instruction = {
            "en": "Respond in English.",
            "fr": "Répondez en français.",
            "de": "Antworten Sie auf Deutsch."
        }
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=f"""You are a helpful assistant that answers questions based ONLY on the provided context.
If the answer is not in the context, say so honestly.
Be concise and helpful. {lang_instruction.get(language, lang_instruction['en'])}""",
            messages=[
                {
                    "role": "user",
                    "content": f"""Context from uploaded documents:
{context}

Question: {query}

Answer based only on the context above:"""
                }
            ]
        )
        
        response = message.content[0].text
        sources = [chunk[:100] + "..." for chunk, score in relevant_chunks if score > 0]
        return response, sources
        
    except Exception as e:
        return f"API Error: {str(e)}", []

# ─── Header ───
st.markdown('<div class="main-title">🤖 DocuChat AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Upload business documents → Ask questions in any language → Get instant AI answers</div>', unsafe_allow_html=True)

# ─── Sidebar ───
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    # API Mode
    mode = st.radio(
        "Mode",
        ["🎯 Demo (no API key needed)", "🔑 Production (Claude API)"],
        help="Demo mode uses built-in sample data. Production mode connects to Claude API."
    )
    
    st.session_state.api_mode = 'demo' if 'Demo' in mode else 'api'
    
    api_key = None
    if st.session_state.api_mode == 'api':
        api_key = st.text_input("Claude API Key", type="password", help="Get your key at console.anthropic.com")
        if not api_key:
            st.warning("Enter your Claude API key to use production mode.")
    
    # Language
    language = st.selectbox(
        "Response Language",
        [("🇬🇧 English", "en"), ("🇫🇷 Français", "fr"), ("🇩🇪 Deutsch", "de")],
        format_func=lambda x: x[0]
    )[1]
    
    st.markdown("---")
    
    # Document upload
    st.markdown("### 📄 Documents")
    
    if st.session_state.api_mode == 'demo':
        st.info("Demo mode: Using sample restaurant data. Switch to Production mode to upload your own documents.")
        
        if st.button("📂 Load Demo Data", use_container_width=True):
            for key, doc in DEMO_KNOWLEDGE.items():
                chunks = chunk_text(doc['content'])
                st.session_state.documents[doc['name']] = {
                    'chunks': chunks,
                    'total_chars': len(doc['content']),
                    'num_chunks': len(chunks)
                }
            st.success(f"Loaded {len(DEMO_KNOWLEDGE)} demo document(s)!")
            st.rerun()
    else:
        uploaded_files = st.file_uploader(
            "Upload documents",
            type=['txt', 'pdf', 'md'],
            accept_multiple_files=True,
            help="Upload TXT, PDF, or Markdown files"
        )
        
        if uploaded_files:
            for file in uploaded_files:
                if file.name not in st.session_state.documents:
                    try:
                        if file.name.endswith('.pdf'):
                            try:
                                import PyPDF2
                                pdf_reader = PyPDF2.PdfReader(file)
                                content = ""
                                for page in pdf_reader.pages:
                                    content += page.extract_text() + "\n"
                            except ImportError:
                                st.warning("Install PyPDF2 for PDF support: pip install PyPDF2")
                                continue
                        else:
                            content = file.read().decode('utf-8')
                        
                        chunks = chunk_text(content)
                        st.session_state.documents[file.name] = {
                            'chunks': chunks,
                            'total_chars': len(content),
                            'num_chunks': len(chunks)
                        }
                        st.success(f"✅ Loaded: {file.name}")
                    except Exception as e:
                        st.error(f"Error loading {file.name}: {e}")
    
    # Show loaded documents
    if st.session_state.documents:
        st.markdown("#### Loaded Documents")
        for name, doc in st.session_state.documents.items():
            st.markdown(f'<span class="doc-badge">📄 {name}</span>', unsafe_allow_html=True)
            st.caption(f"{doc['total_chars']:,} chars • {doc['num_chunks']} chunks")
    
    # Clear chat
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ─── Main Chat Area ───
if not st.session_state.documents:
    # Welcome state
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>📄 1. Upload Documents</h4>
            <p>PDF, TXT, or Markdown files. Product docs, FAQs, menus, manuals — anything text-based.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>💬 2. Ask Questions</h4>
            <p>Ask in natural language. "What are the opening hours?" "Show me vegetarian options." Works in EN/FR/DE.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>🎯 3. Get AI Answers</h4>
            <p>Answers come directly from YOUR documents. No hallucinations — sources are always cited.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("#### 💡 Try these demo questions after loading data:")
    demo_questions = [
        "What vegetarian options do you have?",
        "What are the opening hours?",
        "How much does the filet mignon cost?",
        "Can I book for a group of 10?",
        "Do you handle food allergies?",
        "Quels sont les plats végétariens ?",
        "Was sind die Öffnungszeiten?"
    ]
    
    cols = st.columns(3)
    for i, q in enumerate(demo_questions):
        cols[i % 3].code(q, language=None)

else:
    # Chat interface
    # Display message history
    for msg in st.session_state.messages:
        if msg['role'] == 'user':
            st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bot">{msg["content"]}</div>', unsafe_allow_html=True)
            if msg.get('sources'):
                with st.expander("📎 Sources", expanded=False):
                    for src in msg['sources']:
                        st.markdown(f'<div class="source-ref">{src}</div>', unsafe_allow_html=True)
    
    # Chat input
    user_input = st.chat_input("Ask a question about your documents...")
    
    if user_input:
        # Add user message
        st.session_state.messages.append({'role': 'user', 'content': user_input})
        
        # Search across all documents
        all_chunks = []
        for doc_name, doc_data in st.session_state.documents.items():
            all_chunks.extend(doc_data['chunks'])
        
        # Retrieve relevant chunks
        relevant = simple_search(user_input, all_chunks, top_k=3)
        
        # Generate response
        if st.session_state.api_mode == 'api' and api_key:
            response, sources = generate_api_response(user_input, relevant, api_key, language)
        else:
            response, sources = generate_demo_response(user_input, relevant, language)
        
        # Add bot response
        st.session_state.messages.append({
            'role': 'assistant',
            'content': response,
            'sources': sources
        })
        
        st.rerun()

# ─── Footer ───
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #b2bec3; font-size: 0.8rem;">
    DocuChat AI — RAG-powered document Q&A | Built with Python, Streamlit & Claude API<br>
    <strong>Portfolio project by [YOUR NAME]</strong> | Available for freelance: AI chatbots, automation, data analysis
</div>
""", unsafe_allow_html=True)
