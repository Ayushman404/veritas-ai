import os
import time
from dotenv import load_dotenv

# Import the modules we built across the pipeline
from src.retrieval.pipeline import RetrievalPipeline
from src.generation.generator import LLMGenerator

# Load environment variables (API keys, DB credentials)
load_dotenv(dotenv_path="config/.env")

class RAGApplication:
    def __init__(self):
        print("Initializing Veritas Enterprise RAG Pipeline...")
        # 1. Initialize the Retrieval Engine (Loads BGE embeddings and Cross-Encoder)
        self.retrieval_pipeline = RetrievalPipeline()
        
        # 2. Initialize the Generation Engine (Loads YAML prompt and LLM)
        self.generator = LLMGenerator(prompt_version="v1.0_strict_grounding.yaml")
        print("Pipeline Ready.\n")

    def ask(self, query: str, strategy: str = "hybrid", apply_reranking: bool = True):
        """
        Executes the full RAG lifecycle and calculates latency.
        """
        print(f"--- Processing Query: '{query}' ---")
        start_time = time.time()

        # Step 1: Retrieve & Re-rank
        print(f"Executing Retrieval (Strategy: {strategy}, Re-ranking: {apply_reranking})...")
        retrieval_trace = self.retrieval_pipeline.retrieve(
            query=query, 
            strategy=strategy, 
            apply_reranking=apply_reranking
        )

        if not retrieval_trace["final_chunks"]:
            print("No relevant context found in the database. Aborting generation.")
            return

        # Step 2: Generate & Ground
        print(f"Synthesizing Answer (Prompt Version: {retrieval_trace.get('prompt_version', 'N/A')})...")
        final_trace = self.generator.generate(retrieval_trace)
        
        end_time = time.time()
        latency = round(end_time - start_time, 2)

        # Step 3: Output the Proof of Work
        self._display_results(final_trace, latency)
        
        # Return the trace in case you are calling this from an evaluation script
        return final_trace

    def _display_results(self, trace: dict, latency: float):
        """Formats the terminal output to look like a proper enterprise log."""
        print("\n" + "="*50)
        print("FINAL RESPONSE:")
        print("="*50)
        print(trace["llm_response"])
        print("="*50)
        
        print("\n[TELEMETRY & GROUNDING]")
        print(f"Latency:        {latency} seconds")
        print(f"Prompt Config:  {trace.get('prompt_version')}")
        print(f"Chunks Used:    {len(trace['final_chunks'])}")
        
        print("\n[CITED SOURCES]")
        for i, chunk in enumerate(trace["final_chunks"]):
            # print("+"*50)
            # print(chunk)
            # print("+"*50)
            # Safely extract metadata fields assuming they are dictionaries
            meta = chunk.get("metadata", {})
            source = meta.get("url", meta.get("file_path", "Unknown Source"))
            score = chunk.get("cross_encoder_score", chunk.get("score", "N/A"))
            print(f" {i+1}. {source} (Score: {score})")
        print("="*50 + "\n")
        


if __name__ == "__main__":
    # Ensure your OPENAI_API_KEY (or Groq/Ollama equivalent) is in your .env
    app = RAGApplication()
    
    # Run a test query against the Wikipedia data we ingested earlier
    test_query = "What is the role of the Multi-Head Attention mechanism?"
    
    # We test the ultimate configuration: Hybrid Search + Cross-Encoder Reranking
    app.ask(query=test_query, strategy="hybrid", apply_reranking=True)