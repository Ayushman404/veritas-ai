import yaml
import os
from typing import Dict, Any
# Using ChatOpenAI as a placeholder; you can swap this for ChatGroq or ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_core.prompts import ChatPromptTemplate

class LLMGenerator:
    def __init__(self, prompt_version: str = "v1.0_strict_grounding.yaml"):
        self.prompt_config = self._load_prompt(prompt_version)
        # Initialize your LLM (temperature=0 is mandatory for strict RAG grounding)
        self.llm = ChatGoogleGenerativeAI(
            temperature=0.1, 
            model="gemini-2.5-flash", # Swap with your preferred model
            api_key=os.getenv("GEMINI_API_KEY")
        )
        self.prompt_template = self._build_prompt_template()

    def _load_prompt(self, filename: str) -> Dict[str, Any]:
        """Loads the YAML configuration file."""
        filepath = os.path.join("config", "prompts", filename)
        with open(filepath, "r") as file:
            return yaml.safe_load(file)

    def _build_prompt_template(self) -> ChatPromptTemplate:
        """Converts the YAML strings into a LangChain PromptTemplate."""
        return ChatPromptTemplate.from_messages([
            ("system", self.prompt_config["system_prompt"]),
            ("human", self.prompt_config["user_prompt"])
        ])

    def _format_context(self, chunks: list) -> str:
        formatted_text = ""
        for i, chunk in enumerate(chunks):
            meta = chunk.get("metadata", {})
            
            # Fallback chain: url -> file_path -> Unknown Origin
            source = meta.get("url", meta.get("file_path", "Unknown Origin"))
            section = meta.get("section", "")
            
            # If it's a PDF with sections, append the section to the citation
            citation = f"{source} ({section})" if section else source
            
            formatted_text += f"--- Chunk {i+1} [Source: {citation}] ---\n{chunk['text']}\n\n"
        return formatted_text

    def generate(self, retrieval_trace: Dict[str, Any]) -> Dict[str, Any]:
        """
        The main orchestrator. Takes the retrieval trace, formats the prompt, and gets the answer.
        Returns an enriched trace containing the final answer and prompt version used.
        """
        # 1. Format the retrieved chunks into a single context string
        context_string = self._format_context(retrieval_trace["final_chunks"])
        
        # 2. Prepare the prompt inputs
        chain = self.prompt_template | self.llm
        
        # 3. Execute LLM Inference
        response = chain.invoke({
            "context": context_string,
            "query": retrieval_trace["query"]
        })
        
        # 4. Enrich the trace with generation metadata for evaluation
        retrieval_trace["prompt_version"] = self.prompt_config["version"]
        retrieval_trace["formatted_context"] = context_string
        retrieval_trace["llm_response"] = response.content
        
        return retrieval_trace