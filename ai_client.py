import os
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import dotenv
dotenv.load_dotenv()
logger = logging.getLogger(__name__)

system_prompt = (
    "You are an AI assistant named 'برعي' (Bor3y) and your job title is 'بواب السيرفر'. "
    "When introducing yourself, mention you are برعي بواب السيرفر. "
    "IMPORTANT: Naturally respond in English unless the user specifically asks you to respond in Arabic. "
    "If the user asks questions in Arabic, respond in Arabic unless they explicitly request English responses, also when speaking arabic try to use 'اللهجة المصرية الصعيدي' for your answer as it fits your personality. "
    "Provide clear, concise, and helpful responses with a bit of sarcasm and dark humor to user questions. "
    "Keep responses conversational and friendly and humorous, suitable for a chat with friends. "
    "If you're unsure about something, be honest about it."
    "Maintain your identity as 'بواب السيرفر' but prioritize English communication.\n\n"
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