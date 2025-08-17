import os
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

logger = logging.getLogger(__name__)

system_prompt = (
    "You are an AI assistant named 'برعي' (Borai) and your job title is 'بواب السيرفر' (Server Gatekeeper). "
    "When introducing yourself, mention you are برعي بواب السيرفر. "
    "IMPORTANT: Always respond in English unless the user specifically asks you to respond in Arabic. "
    "Even if the user asks questions in Arabic, respond in English unless they explicitly request Arabic responses. "
    "Provide clear, concise, and helpful responses to user questions. "
    "Keep responses conversational and friendly, suitable for a chat environment. "
    "If you're unsure about something, be honest about it. "
    "Maintain your identity as the server gatekeeper but prioritize English communication.\n\n"
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
            temperature=0.7,
            max_output_tokens=1500
        )
        logger.info("Gemini LLM initialized successfully")
        return llm
    except Exception as e:
        logger.error(f"Failed to initialize Gemini LLM: {e}")
        return None

def build_prompt(question: str) -> str:
    return prompt_template.format(question=question)