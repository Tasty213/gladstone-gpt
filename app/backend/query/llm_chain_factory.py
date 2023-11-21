from pathlib import Path
from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma
from langchain.vectorstores.base import VectorStore
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain.callbacks.base import AsyncCallbackHandler
from settings.chat_bot_settings import ChatbotSettings
import os
import boto3

from langchain.chains.chat_vector_db.prompts import CONDENSE_QUESTION_PROMPT
from langchain.chains.llm import LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from opentelemetry import trace

tracer = trace.get_tracer("chatbot.vortex_query")


class LLMChainFactory:
    @staticmethod
    def download_document_store(settings: ChatbotSettings):
        if not Path(settings.persist_directory).exists():
            LLMChainFactory.download_data(settings)

    @staticmethod
    @tracer.start_as_current_span("chatbot.VortexQuery.download_data")
    def download_data(settings: ChatbotSettings):
        """
        Download the contents of a folder directory
        Args:
            bucket_name: the name of the s3 bucket
            s3_folder: the folder path in the s3 bucket
            local_dir: a relative or absolute directory path in the local file system
        """
        s3 = boto3.resource("s3")
        bucket = s3.Bucket(settings.document_store_bucket)
        for obj in bucket.objects.filter():
            target = (
                obj.key
                if settings.persist_directory is None
                else os.path.join(settings.persist_directory, obj.key)
            )
            if not os.path.exists(os.path.dirname(target)):
                os.makedirs(os.path.dirname(target))
            if obj.key[-1] == "/":
                continue
            bucket.download_file(obj.key, target)

    @staticmethod
    @tracer.start_as_current_span("chatbot.VortexQuery.get_vector_store")
    def get_vector_store(settings: ChatbotSettings) -> VectorStore:
        LLMChainFactory.download_document_store(settings)
        embedding = OpenAIEmbeddings(client=None)

        return Chroma(
            collection_name=settings.collection_name,
            embedding_function=embedding,
            persist_directory=settings.persist_directory,
        )

    @staticmethod
    def get_system_prompt(local_party_details: str, settings: ChatbotSettings) -> str:
        return settings.system_prompt.replace(
            "LOCAL_PARTY_DETAILS_PLACEHOLDER", local_party_details
        )

    @staticmethod
    def get_user_prompt() -> str:
        return "Question:```{question}```"

    @staticmethod
    def get_chat_prompt_template(
        local_party_details: str, settings: ChatbotSettings
    ) -> ChatPromptTemplate:
        system = LLMChainFactory.get_system_prompt(local_party_details, settings)
        user = LLMChainFactory.get_user_prompt()
        messages = [
            SystemMessagePromptTemplate.from_template(system),
            HumanMessagePromptTemplate.from_template(user),
        ]
        return ChatPromptTemplate.from_messages(messages)

    @staticmethod
    @tracer.start_as_current_span("chatbot.VortexQuery.make_chain")
    def make_chain(
        vector_store: VectorStore,
        open_ai_costings_handler: AsyncCallbackHandler,
        otel_handler: AsyncCallbackHandler,
        stream_handler: AsyncCallbackHandler,
        local_party_details: str,
        settings: ChatbotSettings,
    ) -> ConversationalRetrievalChain:
        question_gen_llm = OpenAI(
            temperature=settings.temperature, verbose=True, callbacks=[otel_handler]
        )
        question_generator = LLMChain(
            llm=question_gen_llm,
            prompt=CONDENSE_QUESTION_PROMPT,
            callbacks=[otel_handler, open_ai_costings_handler],
        )

        streaming_llm = ChatOpenAI(
            streaming=True,
            callbacks=[stream_handler, otel_handler, open_ai_costings_handler],
            verbose=True,
            temperature=settings.temperature,
            model=settings.model_name,
            max_tokens=settings.max_tokens,
        )
        doc_chain = load_qa_chain(
            streaming_llm,
            chain_type="stuff",
            prompt=LLMChainFactory.get_chat_prompt_template(
                local_party_details, settings
            ),
            callbacks=[otel_handler, open_ai_costings_handler],
        )

        qa = ConversationalRetrievalChain(
            retriever=vector_store.as_retriever(
                search_type="mmr",
                search_kwargs={
                    "k": settings.documents_returned,
                    "fetch_k": settings.documents_considered,
                    "lambda_mult": settings.lambda_mult,
                },
            ),
            combine_docs_chain=doc_chain,
            question_generator=question_generator,
            return_source_documents=True,
            callbacks=[otel_handler, open_ai_costings_handler],
        )

        return qa
