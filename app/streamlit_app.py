from openai import InvalidRequestError
import streamlit as st
from streamlit_chat import message
from PIL import Image
from query.vortex_query import VortexQuery
from langchain.schema import Document
import json

def initialize_page():
    st.set_page_config(page_title='Gladstone GPT', page_icon=':books:')
    st.image(logo_image, width=80)
    st.header("Gladstone GPT")
    st.write("This is a AI Chatbot with access to the Liberal Democray 2019 manifesto and articles from the party website. You can ask the chatbot any question and it will try to find an answer within the provided documentation. It can't generate new policy and can't argue in favour of policy only state in a concise manor.")
    st.markdown("If the AI produces any content that is incorrect, offence or harmful please contact me on [email](mailto:gsykes537@gmail.com)")
    st.markdown("[Github](https://github.com/Tasty213/gladstone-gpt)")


def handle_query_form() -> tuple[str, bool]:
    with st.form(key='query_form'):
        user_query = st.text_input('Ask Gladstone:', '', key='input',
                                   help='Enter a question about Lib Dem policy.')
        submit_button = st.form_submit_button('Submit')
    return user_query, submit_button


def display_chat_history():
    for i, (user_msg, ai_msg) in enumerate(zip(st.session_state['past'][::-1],
                                               st.session_state['generated'][::-1])):
        message(user_msg, is_user=True, key=f"user_{i}")
        message(ai_msg, key=f"ai_{i}", allow_html = True)


def query(question: str) -> tuple[str, list[Document]]:
    """
    Query the VortexQuery model with the provided question
    :param question: The question to ask the model
    :return: The answer from the model
    """
    vortex_query = VortexQuery()
    answer, source = vortex_query.ask_question(question)
    return answer, source


logo_image = Image.open('./logo.png')

# Initialize page and session state
st.session_state.setdefault('generated', [])
st.session_state.setdefault('past', [])

initialize_page()
user_query, submit_button = handle_query_form()

if submit_button and user_query:
    try:
        answer, sources = query(user_query)
        
        source_text_list = set()
        for source in sources:
            metadata = source.metadata
            source_text = f"[{metadata.get('name')}]({metadata.get('link')})"
            source_text_list.add(source_text)
        source_text = "\n".join(source_text_list)
        
        output_text =f"""{answer}

My sources for this are:
{source_text}"""
        
    except InvalidRequestError as e:
        output_text = "I'm really sorry but your query has returned back too many results, can you try being precise, writing a longer question or refreshing the page?"

    st.session_state.past.append(user_query)
    st.session_state.generated.append(output_text)


display_chat_history()
