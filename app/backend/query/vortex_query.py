from pathlib import Path
import time
from typing import Dict, List
import uuid
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.vectorstores.chroma import Chroma
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from backend.messageData import MessageData
from backend.query.message_factory import MessageFactory
from backend.settings import COLLECTION_NAME, PERSIST_DIRECTORY, MODEL_NAME
import os
import boto3
from hashlib import sha256


class VortexQuery:
    def __init__(self):
        if not Path(PERSIST_DIRECTORY).exists():
            self.download_data()

        self.chain = self.make_chain()

    def download_data(
        self,
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

    def make_chain(self) -> ConversationalRetrievalChain:
        with open("./backend/query/system_prompt.txt", "r") as system_prompt_file:
            general_system_template = "\n".join(system_prompt_file.readlines())

        general_user_template = "Question:```{question}```"
        messages = [
            SystemMessagePromptTemplate.from_template(general_system_template),
            HumanMessagePromptTemplate.from_template(general_user_template),
        ]
        qa_prompt = ChatPromptTemplate.from_messages(messages)

        model = ChatOpenAI(
            client=None,
            model=MODEL_NAME,
            temperature=0.5,
        )
        embedding = OpenAIEmbeddings(client=None)

        vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embedding,
            persist_directory=PERSIST_DIRECTORY,
        )

        return ConversationalRetrievalChain.from_llm(
            model,
            retriever=vector_store.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 4, "fetch_k": 10, "lambda_mult": 0.2},
            ),
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": qa_prompt},
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
