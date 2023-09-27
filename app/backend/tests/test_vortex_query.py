from unittest import mock

from pytest import MonkeyPatch
from query.vortex_query import VortexQuery
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import VectorStore
from langchain.prompts import ChatPromptTemplate
from langchain.callbacks.base import AsyncCallbackHandler
from langchain import llms


def test_download_data():
    pass


def test_get_vector_store():
    vector_store = VortexQuery.get_vector_store()
    assert isinstance(vector_store, VectorStore)


def test_get_system_prompt():
    system_prompt = VortexQuery.get_system_prompt()
    assert isinstance(system_prompt, str)


def test_get_user_prompt():
    user_prompt = VortexQuery.get_user_prompt()
    assert user_prompt == "Question:```{question}```"


def test_get_chat_prompt_template():
    chat_prompt_template = VortexQuery.get_chat_prompt_template()
    assert isinstance(chat_prompt_template, ChatPromptTemplate)


def test_make_chain():
    llms.OpenAI = llms.FakeListLLM
    chain = VortexQuery.make_chain(
        VortexQuery.get_vector_store(),
        AsyncCallbackHandler(),
        AsyncCallbackHandler(),
    )
    assert isinstance(chain, ConversationalRetrievalChain)
