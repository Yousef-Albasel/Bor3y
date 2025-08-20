from discord import app_commands
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import PyPDFLoader
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

async def run_summarizer(file_path: str) -> str:
    loader = PyPDFLoader(file_path)
    docs = loader.load_and_split()
    llm = ChatGroq(
        model="llama3-70b-8192",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.2,
    )
    chain = load_summarize_chain(llm, chain_type="map_reduce")
    result = chain.invoke(docs)
    return result["output_text"]