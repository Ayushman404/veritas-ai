import os
import re
import shutil
from typing import List
from fastapi import UploadFile

# LOADERS
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader

# SPLITTERS & CLEANING
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# VECTOR DB & EMBEDDINGS
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# KEYWORD SEARCH (Hybrid)
from langchain_community.retrievers import BM25Retriever

# --- CONFIG ---
EMBEDDING_MODEL = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
DB_DIR = os.path.join(os.getcwd(), "chroma_db")

# Persistent Vector Store
vector_store = Chroma(persist_directory=DB_DIR, embedding_function=EMBEDDING_MODEL)

# In-Memory Keyword Store (BM25)
bm25_retriever = None
global_chunks = []

# --- UTILS ---
def clean_text(text: str) -> str:
    # Remove citations [1], [edit], and extra spaces
    text = re.sub(r'\[\w+\]', '', text)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def update_retrievers(new_chunks: List[Document]):
    global bm25_retriever, global_chunks
    
    # 1. Add to Chroma (Disk)
    vector_store.add_documents(new_chunks)
    
    # 2. Add to BM25 (Memory)
    global_chunks.extend(new_chunks)
    if global_chunks:
        bm25_retriever = BM25Retriever.from_documents(global_chunks)
        bm25_retriever.k = 3
    
    print(f"--- Index Updated. Total Chunks: {len(global_chunks)} ---")

def clear_knowledge_base():
    """Wipes everything."""
    global bm25_retriever, global_chunks
    print("--- CLEARING KNOWLEDGE BASE ---")
    
    try:
        # Delete from Chroma
        ids = vector_store.get()['ids']
        if ids:
            vector_store.delete(ids)
    except Exception as e:
        print(f"Error clearing Chroma: {e}")
    
    # Reset Memory
    bm25_retriever = None
    global_chunks = []
    return True

# --- HANDLERS ---
async def process_url(url: str):
    print(f"--- Processing URL: {url} ---")
    loader = WebBaseLoader(url)
    docs = loader.load()
    return _split_and_store(docs)

async def process_pdfs(files: List[UploadFile]):
    all_docs = []
    temp_dir = "temp_pdfs"
    os.makedirs(temp_dir, exist_ok=True)

    for file in files:
        print(f"--- Processing PDF: {file.filename} ---")
        temp_path = os.path.join(temp_dir, file.filename)
        
        # Write to disk temporarily
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        loader = PyPDFLoader(temp_path)
        all_docs.extend(loader.load())
    
    # Cleanup
    shutil.rmtree(temp_dir)
    return _split_and_store(all_docs)

def _split_and_store(raw_docs):
    for doc in raw_docs:
        doc.page_content = clean_text(doc.page_content)
        
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(raw_docs)
    
    update_retrievers(chunks)
    return len(chunks)

# --- EXPORTS FOR BRAIN ---
def get_vector_store():
    return vector_store

def get_bm25_retriever():
    return bm25_retriever