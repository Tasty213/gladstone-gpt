from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import AIMessage, HumanMessage, Document
from langchain.vectorstores.chroma import Chroma
from langchain import PromptTemplate
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from settings import COLLECTION_NAME, PERSIST_DIRECTORY


class VortexQuery:
    def __init__(self):
        load_dotenv()
        self.chain = self.make_chain()
        self.chat_history = []

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
                    HumanMessagePromptTemplate.from_template(general_user_template)
        ]
        qa_prompt = ChatPromptTemplate.from_messages( messages )
        
        model = ChatOpenAI(
            client=None,
            model="gpt-3.5-turbo",
            temperature=0,
        )
        embedding = OpenAIEmbeddings(client=None)

        vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embedding,
            persist_directory=PERSIST_DIRECTORY
        )

        return ConversationalRetrievalChain.from_llm(
            model,
            retriever=vector_store.as_retriever(),
            return_source_documents=True,
            combine_docs_chain_kwargs={'prompt': qa_prompt}
        )

    def ask_question(self, question: str) -> tuple[str, list[Document]]:
        response = self.chain({"question": question, "chat_history": self.chat_history})

        answer = response.get("answer")
        source = response.get("source_documents")
        self.chat_history.append(HumanMessage(content=question))
        self.chat_history.append(AIMessage(content=answer))

        return answer, source
