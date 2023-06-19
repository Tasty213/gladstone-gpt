import streamlit as st
from streamlit_chat import message
from PIL import Image
from query.vortex_query import VortexQuery
import json

def initialize_page():
    st.set_page_config(page_title='Gladstone GPT', page_icon=':books:')
    st.image(logo_image, width=80)
    st.header("Gladstone GPT")
    st.write("This is a AI Chatbot with access to the Liberal Democray 2019 manifesto and articles from the party website. You can ask the chatbot any question and it will try to find an answer within the provided documentation. It can't generate new policy and can't argue in favour of policy only state in a concise manor.")
    st.markdown("If the AI produces any content that is incorrect, offence or harmful please contact me on [email](mailto:gsykes537@gmail.com)")
    st.markdown("[Github](https://github.com/Tasty213/gladstone-gpt)")


def handle_query_form():
    with st.form(key='query_form'):
        user_query = st.text_input('Ask Gladstone:', '', key='input',
                                   help='Enter a question about Lib Dem policy.')
        submit_button = st.form_submit_button('Submit')
    return user_query, submit_button


def display_chat_history():
    for i, (user_msg, ai_msg) in enumerate(zip(st.session_state['past'][::-1],
                                               st.session_state['generated'][::-1])):
        message(user_msg, is_user=True, key=f"user_{i}")
        message(ai_msg, key=f"ai_{i}")


def query(question: str) -> str:
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
    answer, source = query(user_query)
    st.session_state.past.append(user_query)
    st.session_state.generated.append(answer)

display_chat_history()
