from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from core.config import OPENROUTER_API_KEY, MODEL_NAME, OPENROUTER_BASE_URL
from tools.document import pencarian_dokumen
from agents.prompts import SYSTEM_PROMPT

def get_r2cell_agent():
    llm = ChatOpenAI(
        openai_api_base=OPENROUTER_BASE_URL,
        openai_api_key=OPENROUTER_API_KEY,
        model_name=MODEL_NAME,
    )
    tools = [pencarian_dokumen]
    return create_agent(llm, tools, system_prompt=SYSTEM_PROMPT)
