import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# LOCAL MODULES
from .ingestion import get_vector_store, get_bm25_retriever

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# USE FLASH (Faster) or PRO (Smarter)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.3
)

# --- MANUAL ENSEMBLE RETRIEVER (Zero Imports) ---
class SimpleEnsembleRetriever:
    """
    Manually merges results from Vector Search and Keyword Search.
    Replaces the broken 'langchain.retrievers.EnsembleRetriever'.
    """
    def __init__(self, retrievers, weights):
        self.retrievers = retrievers
        self.weights = weights

    def invoke(self, query: str):
        # 1. Fetch from Vector DB
        docs_a = self.retrievers[0].invoke(query)
        # 2. Fetch from BM25 (Keywords)
        docs_b = self.retrievers[1].invoke(query)
        
        # 3. Merge and Deduplicate
        seen_content = set()
        unique_docs = []
        
        # Simple weighted merge: just take unique docs from both
        for doc in docs_a + docs_b:
            if doc.page_content not in seen_content:
                unique_docs.append(doc)
                seen_content.add(doc.page_content)
        
        # Return top 5 distinct results
        return unique_docs[:5]

# --- 1. QUERY REWRITER ---
async def rewrite_query(query: str, history: list):
    if not history:
        return query  
    
    history_str = "\n".join([f"User: {h[0]}\nAI: {h[1]}" for h in history])
    
    template = """
    Given the conversation history, rewrite the follow-up question to be a standalone question.
    Chat History:
    {history}
    Follow Up Input: {question}
    Standalone Question:"""
    
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    
    try:
        return chain.invoke({"history": history_str, "question": query})
    except Exception:
        return query # Fallback

# --- 2. ANSWER GENERATOR ---
async def generate_answer(query: str):
    # A. Setup Retrievers
    vector_store = get_vector_store()
    bm25 = get_bm25_retriever()
    
    vector_retriever = vector_store.as_retriever(search_kwargs={'k': 4})
    
    # Hybrid Search Logic
    if bm25:
        # USE OUR CUSTOM CLASS
        retriever = SimpleEnsembleRetriever(
            retrievers=[bm25, vector_retriever], 
            weights=[0.5, 0.5]
        )
    else:
        retriever = vector_retriever

    # B. Retrieve Docs
    docs = retriever.invoke(query)
    
    # C. Format Context
    if not docs:
        return "I could not find any relevant information in the uploaded documents.", []
        
    context_text = "\n\n".join([d.page_content for d in docs])
    evidence_list = [d.page_content for d in docs]

    # D. Generate Answer
    template = """
    You are Veritas, a research assistant.
    Answer the question based ONLY on the following context.
    If the answer is not in the context, say you don't know.

    Context:
    {context}

    Question: 
    {question}

    Answer:
    """
    
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    
    answer = chain.invoke({"context": context_text, "question": query})
    
    return answer, evidence_list