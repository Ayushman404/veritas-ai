import json
import os
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from app import RAGApplication
from langchain_google_genai import ChatGoogleGenerativeAI
from ragas.llms import LangchainLLMWrapper
from langchain_huggingface import HuggingFaceEmbeddings
from ragas.embeddings import LangchainEmbeddingsWrapper


def run_evaluation():
    print("1. Loading RAG Pipeline...")
    app = RAGApplication()
    
    print("\n2. Loading Golden Dataset...")
    with open("data/golden_dataset.json", "r") as f:
        qa_pairs = json.load(f)
        
    data_samples = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": []
    }
    
    print(f"\n3. Running Pipeline on {len(qa_pairs)} queries (This will take a while)...")
    for item in qa_pairs:
        # Run your actual pipeline
        trace = app.ask(query=item["question"], strategy="hybrid", apply_reranking=True)
        
        # Format the data exactly how Ragas expects it
        data_samples["question"].append(item["question"])
        data_samples["answer"].append(trace["llm_response"])
        # Ragas expects a list of strings for contexts
        data_samples["contexts"].append([chunk["text"] for chunk in trace["final_chunks"]])
        data_samples["ground_truth"].append(item["ground_truth"])
        
    # Convert to HuggingFace Dataset format
    dataset = Dataset.from_dict(data_samples)
    
    print("\n4. Initializing Gemini Evaluator Models...")
    # Initialize your free tier Gemini models
    gemini_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    wrapped_llm = LangchainLLMWrapper(gemini_llm)
    
    hf_embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-base-en-v1.5",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    wrapped_embeddings = LangchainEmbeddingsWrapper(hf_embeddings)
    
    print("\n4. Running Ragas Evaluation...")
    # This calls OpenAI to grade your pipeline's performance
    results = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision],
        llm=wrapped_llm,
        embeddings=wrapped_embeddings
    )
    
    print("\n" + "="*50)
    print("FINAL EVALUATION SCORES:")
    print("="*50)
    print(results)
    
    # Save the results to a file for your resume documentation
    results.to_pandas().to_csv("evaluation_report.csv", index=False)
    print("Report saved to evaluation_report.csv")

if __name__ == "__main__":
    run_evaluation()