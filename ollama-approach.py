import os
from pathlib import Path
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
)
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

def main():
    llm = Ollama(model="llama2", temperature=0.1, request_timeout=120.0)
    embed_model = OllamaEmbedding(model_name="llama2")

    documents = SimpleDirectoryReader("annual-reports").load_data()
    index = VectorStoreIndex.from_documents(
        documents,
        llm=llm,
        embed_model=embed_model
    )

    query_engine = index.as_query_engine()
    response = query_engine.query("You are CFO-GPT. Quickly answer which of the companies has more liquidity and how much exactly. Use annual reports. Don't make up information if you're not certain")
    print(response)

if __name__ == "__main__":
    main() 