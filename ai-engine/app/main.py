from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from app.models import QueryRequest
from app.services import ingestion, brain

app = FastAPI()

# Enable CORS for direct Frontend access (Bypassing broken Node)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "Veritas Brain Online"}

@app.post("/ingest/url")
async def ingest_url(url: str = Form(...)):
    count = await ingestion.process_url(url)
    return {"status": "success", "chunks_stored": count}

@app.post("/ingest/pdf")
async def ingest_pdf(files: List[UploadFile] = File(...)):
    count = await ingestion.process_pdfs(files)
    return {"status": "success", "chunks_stored": count}

@app.delete("/reset")
async def reset_brain():
    ingestion.clear_knowledge_base()
    return {"status": "success", "message": "Memory Wiped."}

@app.post("/ask")
async def ask(request: QueryRequest):
    try:
        # 1. Rewrite Query (Context)
        rewritten_q = await brain.rewrite_query(request.query, request.chat_history)
        
        # 2. Generate Answer (RAG)
        answer, evidence = await brain.generate_answer(rewritten_q)
        
        return {
            "query": request.query,
            "rewritten_query": rewritten_q,
            "answer": answer,
            "evidence": evidence
        }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))