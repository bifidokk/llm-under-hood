import os
import openai
from pathlib import Path
from dotenv import load_dotenv

from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
)

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

def main():
    documents = SimpleDirectoryReader("annual-reports").load_data()
    index = VectorStoreIndex.from_documents(documents)

    query_engine = index.as_query_engine()
    response = query_engine.query("You are CFO-GPT. Quickly answer which company has more liquidity and how much exactly. Answer with company name and value. Use annual reports. Don't make up information if you're not certain")
    print(response)

if __name__ == "__main__":
    main()

