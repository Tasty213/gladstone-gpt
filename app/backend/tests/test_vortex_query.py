from settings.chat_bot_settings import ChatbotSettings
from query.vortex_query import VortexQuery
from langchain.prompts import ChatPromptTemplate


def test_download_data():
    pass


def test_get_system_prompt(mock_settings: ChatbotSettings):
    system_prompt = VortexQuery.get_system_prompt("", mock_settings)
    assert isinstance(system_prompt, str)


def test_get_user_prompt():
    user_prompt = VortexQuery.get_user_prompt()
    assert user_prompt == "Question:```{question}```"


def test_get_chat_prompt_template(mock_settings: ChatbotSettings):
    chat_prompt_template = VortexQuery.get_chat_prompt_template("", mock_settings)
    assert isinstance(chat_prompt_template, ChatPromptTemplate)
