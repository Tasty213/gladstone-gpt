from pathlib import Path
import time
from typing import Dict, List
import uuid
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.vectorstores.chroma import Chroma
from langchain.vectorstores.base import VectorStore
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain.callbacks.base import AsyncCallbackHandler
from langchain.callbacks.manager import AsyncCallbackManager
from messageData import MessageData
from query.message_factory import MessageFactory
from settings import COLLECTION_NAME, PERSIST_DIRECTORY, MODEL_NAME
import os
import boto3
from opentelemetry import trace

from langchain.chains.chat_vector_db.prompts import CONDENSE_QUESTION_PROMPT, QA_PROMPT
from langchain.chains.llm import LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI


class VortexQuery:
    def __init__(self):
        if not Path(PERSIST_DIRECTORY).exists():
            self.download_data()

    @staticmethod
    def download_data(
        bucket_name="gladstone-gpt-data",
        local_dir=PERSIST_DIRECTORY,
    ):
        """
        Download the contents of a folder directory
        Args:
            bucket_name: the name of the s3 bucket
            s3_folder: the folder path in the s3 bucket
            local_dir: a relative or absolute directory path in the local file system
        """
        s3 = boto3.resource("s3")
        bucket = s3.Bucket(bucket_name)
        for obj in bucket.objects.filter():
            target = obj.key if local_dir is None else os.path.join(local_dir, obj.key)
            if not os.path.exists(os.path.dirname(target)):
                os.makedirs(os.path.dirname(target))
            if obj.key[-1] == "/":
                continue
            bucket.download_file(obj.key, target)

    @staticmethod
    def get_vector_store() -> VectorStore:
        embedding = OpenAIEmbeddings(client=None)

        return Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embedding,
            persist_directory=PERSIST_DIRECTORY,
        )

    @staticmethod
    def get_system_prompt() -> str:
        with open("./query/system_prompt.txt", "r") as system_prompt_file:
            general_system_template = "\n".join(system_prompt_file.readlines())
        return general_system_template

    @staticmethod
    def get_user_prompt() -> str:
        return "Question:```{question}```"

    @staticmethod
    def get_chat_prompt_template() -> ChatPromptTemplate:
        system = VortexQuery.get_system_prompt()
        user = VortexQuery.get_user_prompt()
        messages = [
            SystemMessagePromptTemplate.from_template(system),
            HumanMessagePromptTemplate.from_template(user),
        ]
        return ChatPromptTemplate.from_messages(messages)

    BASE_LLM = ChatOpenAI(
        client=None, model=MODEL_NAME, temperature=0.5, streaming=True, verbose=True
    )

    @staticmethod
    def make_chain(
        vector_store: VectorStore,
        question_handler: AsyncCallbackHandler,
        stream_handler: AsyncCallbackHandler,
        tracing: bool = True,
    ) -> ConversationalRetrievalChain:
        qa_prompt = VortexQuery.get_chat_prompt_template()

        """Create a ChatVectorDBChain for question/answering."""
        # Construct a ChatVectorDBChain with a streaming llm for combine docs
        # and a separate, non-streaming llm for question generation
        manager = AsyncCallbackManager([])
        question_manager = AsyncCallbackManager([question_handler])
        stream_manager = AsyncCallbackManager([stream_handler])
        # if tracing:
        #     tracer = LangChainTracer()
        #     tracer.load_default_session()
        #     manager.add_handler(tracer)
        #     question_manager.add_handler(tracer)
        #     stream_manager.add_handler(tracer)

        question_gen_llm = OpenAI(
            temperature=0,
            verbose=True,
            callback_manager=question_manager,
        )
        streaming_llm = OpenAI(
            streaming=True,
            callback_manager=stream_manager,
            verbose=True,
            temperature=0,
        )

        question_generator = LLMChain(
            llm=question_gen_llm,
            prompt=CONDENSE_QUESTION_PROMPT,
            callback_manager=manager,
        )
        doc_chain = load_qa_chain(
            streaming_llm,
            chain_type="stuff",
            prompt=QA_PROMPT,
            callback_manager=manager,
        )

        qa = ConversationalRetrievalChain(
            retriever=vector_store.as_retriever(),
            combine_docs_chain=doc_chain,
            question_generator=question_generator,
            callback_manager=manager,
        )
        return qa

        return ConversationalRetrievalChain.from_llm(
            VortexQuery.BASE_LLM,
            retriever=vector_store.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 4, "fetch_k": 10, "lambda_mult": 0.2},
            ),
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": qa_prompt},
            callback_manager=stream_handler,
        )

    @trace.get_tracer("opentelemetry.instrumentation.custom").start_as_current_span(
        "VortexQuery.ask_question"
    )
    def ask_question(
        self, input: List[Dict], table: MessageData
    ) -> tuple[str, list[Document]]:
        chat_history = list(map(lambda x: MessageFactory.create_message(x), input[:-1]))
        question = input[-1]
        table.add_message(
            question.get("messageId"),
            question.get("userId"),
            question.get("content"),
            question.get("source"),
            question.get("time"),
            question.get("previousMessageId"),
        )
        response = self.chain(
            {
                "question": question.get("content"),
                "chat_history": chat_history,
            }
        )
        answer = response.get("answer")
        sources: List[Document] = response.get("source_documents")
        source_metadata = [source.metadata for source in sources]
        messageId = str(uuid.uuid4())

        table.add_message(
            messageId,
            "AI",
            answer,
            source_metadata,
            round(time.time() * 1000),
            question.get("messageId"),
        )

        return {
            "status": "SUCCESS",
            "answer": answer,
            "sources": source_metadata,
            "previousMessageId": question.get("messageId"),
            "messageId": messageId,
        }
