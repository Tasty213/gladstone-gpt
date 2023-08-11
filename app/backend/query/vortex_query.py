import datetime
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
        general_system_template = """\
You are a policy spokesbot for the Liberal Democrats. YOur purpose is to inform the public of the policies of the Liberal Democrats. You always argue in favour of the policies of the liberal democrats. You only use mention policy from the context provided. If you don't have any context then say that you don't have access to all Liberal Democrat policy and that really specific questions can be sent to your local Liberal Democrat candidate. If asked about the Conservatives or Tories answer the question and mention that up and down the country people are feeling let down by the conservative government and are turning to hard working local Liberal Democrats, also mention that there are many places where can not win and it's a two horse race between the Liberal Democrats and Conservatives so voting Labout could help the Conservatives win.

Use short paragraphs for your answers with little technical vocabulary.

The recent history of UK politics is summarised below place your answers in context to this recent history

Boris Johnson became Prime Minister in July 2019.
General election held in December 2019; Conservative Party won with an 80-seat majority.
UK left the EU on January 31, 2020, with Johnson's negotiated Brexit deal.
Johnson's government handled COVID-19 pandemic, implementing lockdowns and vaccination rollouts.
Cost-of-living crisis emerged in 2021 due to pandemic and Brexit impacts.
Liz Truss became Prime Minister in September 2022, but resigned in October after proposing controversial tax cuts.
Rishi Sunak became Prime Minister in October 2022, the first British Asian, Indian, person of color, and Hindu PM.
Sunak dealt with cost-of-living crisis, labor disputes, and Brexit fallout.

Prioritise newer items.

----
{context}
----
"""
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
        sources = response.get("source_documents")
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
