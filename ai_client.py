import os
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_community.retrievers import TavilySearchAPIRetriever
from langchain.chains import RetrievalQA

import dotenv
dotenv.load_dotenv()
logger = logging.getLogger(__name__)

retriever = TavilySearchAPIRetriever(api_key=os.environ.get("TAVILY_API_KEY"))
system_prompt = (
    "You are an AI assistant named 'برعي' (Bor3y) and your job title is 'بواب السيرفر'. "
    "When introducing yourself, mention you are برعي بواب السيرفر. "
    "IMPORTANT: Naturally respond in English unless the user specifically asks you to respond in Arabic. "
    "If the user asks questions in Arabic, respond in Arabic, also when speaking arabic try to use 'اللهجة المصرية الصعيدي' for your answer as it fits your personality, also with serious questions don't make jokes. "
    "Provide clear, concise, and helpful responses with a bit of sarcasm and dark humor to user questions. "
    "Keep responses conversational and friendly, suitable for a chat with friends. "
    "If you're unsure about something, be honest about it."
    "Maintain your identity as 'بواب السيرفر'.\n\n"
    "User question: {question}"
)
prompt_template = PromptTemplate(
    input_variables=["question"],
    template=system_prompt
)

def get_gemini_llm():
    try:
        llm = ChatGoogleGenerativeAI(
            google_api_key=os.environ.get("GEMINI_API_KEY"),
            model="gemini-1.5-flash",
            temperature=0.7
        )
        logger.info("Gemini LLM initialized successfully")
        return llm
    except Exception as e:
        logger.error(f"Failed to initialize Gemini LLM: {e}")
        return None

def build_prompt(question: str) -> str:
    return prompt_template.format(question=question)


def get_search_chain():
    retriever = TavilySearchAPIRetriever(api_key=os.environ.get("TAVILY_API_KEY"))
    return RetrievalQA.from_chain_type(
        llm=get_gemini_llm(),
        retriever=retriever,
        return_source_documents=True
    )