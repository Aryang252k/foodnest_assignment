import streamlit as st
from langchain_core.messages import AIMessage,HumanMessage
from model import get_response,final_response


if "chat_history" not in st.session_state:
    st.session_state.chat_history=[
        AIMessage(content="Hello! I'm a food supplier chatbot. Order foods now."),
    ]

st.set_page_config(page_title="Food_nest_chatbot",page_icon=":sppech_balloon:")
st.title("Food_nest_chatbot")

for message in st.session_state.chat_history:
    if isinstance(message,AIMessage):
        with st.chat_message("AI"):
            st.markdown(message.content)
    elif isinstance(message,HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)


user_query=st.chat_input("Type a meesage...")

if user_query is not None and user_query.strip()!='':
    st.session_state.chat_history.append(HumanMessage(content=user_query))

    with st.chat_message("Human"):
        st.markdown(user_query)

    with st.chat_message("AI"):
        query=get_response(user_query)
        response=final_response(query=query,question=user_query,history=st.session_state.chat_history)
        st.markdown(response)


    st.session_state.chat_history.append(AIMessage(content=response))
