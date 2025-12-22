import os
import re
from typing import List, Tuple
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# RAG & Vector DB
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# HYBRID SEARCH IMPORTS
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever

# Generative AI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

app = FastAPI()

# --- 1. CONFIGURATION ---

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
DB_DIR = os.path.join(os.getcwd(), "chroma_db")
vector_store = Chroma(persist_directory=DB_DIR, embedding_function=embedding_model)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0.2)

# --- GLOBAL MEMORY FOR HYBRID SEARCH ---
# Since BM25 is in-memory, we keep track of chunks here.
global_chunks = []
bm25_retriever = None

# --- 2. UTILITY FUNCTIONS ---

def clean_text(text: str) -> str:
    text = re.sub(r'\[\w+\]', '', text)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def update_hybrid_retriever(new_chunks):
    """
    Rebuilds the BM25 index whenever new data is added.
    """
    global global_chunks, bm25_retriever
    
    # Add new chunks to our global memory
    global_chunks.extend(new_chunks)
    
    print(f"--- Rebuilding BM25 Index with {len(global_chunks)} total chunks ---")
    # Initialize BM25 with all current documents
    bm25_retriever = BM25Retriever.from_documents(global_chunks)
    # k=3 for BM25
    bm25_retriever.k = 3

# --- 3. DATA MODELS ---

class IngestRequest(BaseModel):
    url: str

class QueryRequest(BaseModel):
    query: str
    chat_history: List[Tuple[str, str]] = []

# --- 4. ENDPOINTS ---

@app.get("/")
def read_root():
    return {"status": "Veritas AI Brain is Active"}

@app.post("/ingest")
async def ingest_url(request: IngestRequest):
    try:
        print(f"--- Ingesting: {request.url} ---")
        loader = WebBaseLoader(request.url)
        raw_documents = loader.load()
        
        for doc in raw_documents:
            doc.page_content = clean_text(doc.page_content)
            
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(raw_documents)
        
        # 1. Save to Vector DB (Persistent)
        vector_store.add_documents(chunks)
        
        # 2. Update BM25 Index (In-Memory)
        update_hybrid_retriever(chunks)
        
        return {"status": "success", "chunks_stored": len(chunks)}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_question(request: QueryRequest):
    try:
        current_query = request.query
        
        # --- STEP 1: QUERY REWRITING (Memory) ---
        if request.chat_history:
            history_str = "\n".join([f"User: {h[0]}\nAI: {h[1]}" for h in request.chat_history])
            rewrite_template = """
            Given the conversation history, rewrite the follow-up question to be standalone.
            History: {chat_history}
            Follow Up: {question}
            Standalone Question:"""
            rewrite_prompt = PromptTemplate(template=rewrite_template, input_variables=["chat_history", "question"])
            rewrite_chain = LLMChain(llm=llm, prompt=rewrite_prompt)
            current_query = rewrite_chain.run(chat_history=history_str, question=request.query)
            print(f"Rewritten Query: {current_query}")

        # --- STEP 2: HYBRID RETRIEVAL (The Ensemble) ---
        # Initialize Vector Retriever
        vector_retriever = vector_store.as_retriever(search_kwargs={'k': 3})
        
        # Check if we have BM25 data (we might not if server just restarted)
        if bm25_retriever is not None:
            print("--- Using Hybrid Search (BM25 + Vector) ---")
            # WEIGHTS: 0.5 = 50% keyword match, 50% semantic match
            ensemble_retriever = EnsembleRetriever(
                retrievers=[bm25_retriever, vector_retriever], 
                weights=[0.5, 0.5]
            )
            relevant_docs = ensemble_retriever.get_relevant_documents(current_query)
        else:
            print("--- Warning: BM25 empty. Falling back to Vector Search only ---")
            relevant_docs = vector_retriever.get_relevant_documents(current_query)

        context_text = "\n\n".join([doc.page_content for doc in relevant_docs])
        
        # --- STEP 3: GENERATION ---
        prompt_template = """
        You are Veritas, a high-level Research Architect. 
        Answer the user's question based ONLY on the context below.
        
        Context:
        {context}

        Question: 
        {question}

        Technical Answer:
        """
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        chain = LLMChain(llm=llm, prompt=prompt)
        ai_response = chain.run(context=context_text, question=current_query)
        
        return {
            "query": request.query,
            "rewritten_query": current_query,
            "answer": ai_response,
            "evidence": [doc.page_content for doc in relevant_docs]
        }
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))