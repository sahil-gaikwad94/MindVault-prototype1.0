'''MindVault Prototype - A Simple Personal Knowledge System
This prototype demonstrates:
1. Document ingestion (text files)
2. Semantic search using embeddings
3. AI-powered responses using retrieved context
'''

import streamlit as st
import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path
import hashlib

# For this prototype, I'll simulate embeddings and AI responses
# In the full version, I'll use the actual models

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class MindVaultPrototype:
    def __init__(self, db_path="mindvault.db"):
        self.db_path = db_path
        self.init_database()
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        
    def init_database(self):
        """Initialize SQLite database for storing documents and metadata"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                file_path TEXT,
                content_hash TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                chunk_text TEXT NOT NULL,
                chunk_index INTEGER,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def chunk_text(self, text, chunk_size=500, overlap=50):
        """Split text into overlapping chunks for better retrieval"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
            
        return chunks
    
    def add_document(self, title, content, file_path=None, tags=None):
        """Add a document to the knowledge base"""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try: 
            cursor.execute('''
                INSERT INTO documents (title, content, file_path, content_hash, tags)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, content, file_path, content_hash, tags))
            
            document_id = cursor.lastrowid
            
            # Create chunks and store them
            chunks = self.chunk_text(content)
            for i, chunk in enumerate(chunks):
                cursor.execute('''
                    INSERT INTO chunks (document_id, chunk_text, chunk_index)
                    VALUES (?, ?, ?)
                ''', (document_id, chunk, i))
            
            conn.commit()
            return document_id
        
        except sqlite3.IntegrityError:
            return None  # Document already exists
        finally:
            conn.close()
    
    def search_documents(self, query, limit=5):
        """Search for relevant document chunks using TF-IDF similarity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all chunks
        cursor.execute('''
            SELECT c.chunk_text, d.title, d.created_at, c.document_id
            FROM chunks c
            JOIN documents d ON c.document_id = d.id
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return []
        
        # Extract chunk texts and metadata
        chunk_texts = [r[0] for r in results]
        metadata = [(r[1], r[2], r[3]) for r in results]  # title, date, doc_id
        
        # Compute TF-IDF similarities
        try:
            # Fit vectorizer on all chunks + query
            all_texts = chunk_texts + [query]
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            # Query vector is the last one
            query_vector = tfidf_matrix[-1]
            chunk_vectors = tfidf_matrix[:-1]
            
            # Compute similarities
            similarities = cosine_similarity(query_vector, chunk_vectors).flatten()
            
            # Get top results
            top_indices = similarities.argsort()[-limit:][::-1]
            
            search_results = []
            for idx in top_indices:
                if similarities[idx] > 0.1:
                    search_results.append({
                        'content': chunk_texts[idx],
                        'title': metadata[idx][0],
                        'date': metadata[idx][1],
                        'document_id': metadata[idx][2],
                        'relevance': similarities[idx]
                    })
            
            return search_results
        
        except Exception as e:
            st.error(f"Search error: {e}")
            return []
        
    def generate_response(self, query, search_results):
        """Generate AI-like response using retrieved context (simplified)"""
        if not search_results:
            return "I couldn't find any relevant information in your knowledge base for that query."
        
        # Combine top results for context
        context = "\n\n".join([f"From '{r['title']}': {r['content']}" for r in search_results[:3]])
        
        # Simple response generation (in real version, I'll use local LLM)
        response = f"""Based on your personal knowledge base, here's what I found:

**Context from your documents:**
{context}

**Summary:**
I found {len(search_results)} relevant pieces of information related to your query "{query}". The most relevant content comes from: {', '.join(set(r['title'] for r in search_results[:3]))}.

*Note: This is a simplified response. In the full version, a local AI model would analyze this context and provide more intelligent answers.*"""
        
        return response
    
    def get_all_documents(self):
        """Get list of all documents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, created_at,
                   LENGTH(content) as content_length,
                   SUBSTR(content, 1, 100) as preview
            FROM documents
            ORDER BY created_at DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': r[0],
                'title': r[1],
                'date': r[2],
                'length': r[3],
                'preview': r[4] + '...' if len(r[4]) == 100 else r[4]
            }
            for r in results
        ]

def main():
    st.set_page_config(
        page_title="MindVault Prototype",
        page_icon="🧠",
        layout="wide"
    )
    
    st.title("🧠 MindVault - Your Personal Knowledge OS")
    st.caption("Prototype version - Store, search, and query your personal knowledge")
    
    # Initialize MindVault
    if 'mindvault' not in st.session_state:
        st.session_state.mindvault = MindVaultPrototype()
        
    mv = st.session_state.mindvault
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["💬 Chat", "📄 Documents", "➕ Add Content"])
    
    if page == "💬 Chat":
        st.header("Chat with Your Knowledge")
        
        # Query input
        query = st.text_input("Ask anything about your stored knowledge:",
                              placeholder="What did I write about AI safety?")
        if query:
            with st.spinner("Searching your knowledge base..."):
                results = mv.search_documents(query)
                response = mv.generate_response(query, results)
                
            st.write("### Response")
            st.write(response)
            
            if results:
                st.write("### Sources")
                for i, result in enumerate(results[:3]):
                    with st.expander(f"📄 {result['title']} (relevance: {result['relevance']:.2f})"):
                        st.write(result['content'])
                        st.caption(f"Added: {result['date']}")
                        
    elif page == "📄 Documents":
        st.header("Your Knowledge Base")
        
        docs = mv.get_all_documents()
        
        if docs:
            st.write(f"**{len(docs)} documents** in your knowledge base:")
            
            for doc in docs:
                with st.expander(f"📄 {doc['title']}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(doc['preview'])
                    with col2:
                        st.caption(f"Added: {doc['date']}")
                        st.caption(f"Length: {doc['length']} chars")
                        
        else:
            st.info("No documents yet. Add some content to get started!")
            
    elif page == "➕ Add Content":
        st.header("Add New Content")
        
        tab1, tab2 = st.tabs(["📝 Text", "📁 File Upload"])
        
        with tab1:
            st.subheader("Add Text Content")
            title = st.text_input("Title:")
            content = st.text_area("Content:", height=300)
            tags = st.text_input("Tags (optional):", placeholder="ai, research, notes")
            
            if st.button("Add to Knowledge Base"):
                if title and content:
                    doc_id = mv.add_document(title, content, tags=tags)
                    if doc_id:
                        st.success(f"✅ Added '{title}' to your knowledge base!")
                        st.balloons()
                    else:
                        st.warning("This content already exists in your knowledge base.")
                else:
                    st.error("Please provide both title and content.")
                    
        with tab2:
            st.subheader("Upload Files")
            uploaded_file = st.file_uploader("Choose a file", type=['txt', 'md'])
            
            if uploaded_file:
                content = uploaded_file.read().decode('utf-8')
                title = uploaded_file.name
                
                st.write("**Preview:**")
                st.text(content[:500] + "..." if len(content) > 500 else content)
                
                if st.button("Add File to Knowledge Base"):
                    doc_id = mv.add_document(title, content, file_path=uploaded_file.name)
                    if doc_id:
                        st.success(f"✅ Added '{title}' to your knowledge base!")
                        st.balloons()
                    else:
                        st.warning("This file already exists in your knowledge base.")
                        
    # Footer
    st.sidebar.markdown("---")   
    st.sidebar.markdown("### About")  
    st.sidebar.info("""
    This is a PROTOTYPE of MindVault - Your Personal Knowledge OS.

    **Current Features:**
    - Text document storage
    - Semantic search
    - Simple AI responses

    **In Next Version:**
    - Local LLM integration
    - PDF support
    - Web clipping
    - Memory workflows
    """)

if __name__ == "__main__":
    main()