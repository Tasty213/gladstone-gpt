from settings.chat_bot_settings import ChatbotSettings
from query.llm_chain_factory import LLMChainFactory
from langchain.prompts import ChatPromptTemplate


def test_get_chat_prompt_template(mock_settings: ChatbotSettings):
    chat_prompt_template = LLMChainFactory.get_chat_prompt_template(mock_settings)
    assert isinstance(chat_prompt_template, ChatPromptTemplate)
