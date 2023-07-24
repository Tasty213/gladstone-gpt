from pathlib import Path
from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import AIMessage, HumanMessage, Document
from langchain.vectorstores.chroma import Chroma
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from ..settings import COLLECTION_NAME, PERSIST_DIRECTORY
import os
import boto3


class VortexQuery:
    def __init__(self):
        load_dotenv()

        if not Path(PERSIST_DIRECTORY).exists():
            self.download_data()

        self.chain = self.make_chain()
        self.chat_history = []

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
----
Context: {context}
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
            model="gpt-3.5-turbo",
            temperature=0,
        )
        embedding = OpenAIEmbeddings(client=None)

        vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embedding,
            persist_directory=PERSIST_DIRECTORY,
        )

        return ConversationalRetrievalChain.from_llm(
            model,
            retriever=vector_store.as_retriever(),
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": qa_prompt},
        )

    def ask_question(self, question: str) -> tuple[str, list[Document]]:
        response = self.chain({"question": question, "chat_history": self.chat_history})

        answer = response.get("answer")
        source = response.get("source_documents")
        self.chat_history.append(HumanMessage(content=question))
        self.chat_history.append(AIMessage(content=answer))

        return answer, source
