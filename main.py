import streamlit as st
from rag import answer_question
from rag import test_db

st.set_page_config(
    page_title="Guyana Constitution NL Query",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Ask The Constitution")

with st.sidebar:

    st.header("Document")

    st.page_link(
        "https://www.aramotar.com",
        label="Alexei's Home Page"
    )

    st.page_link(
        "https://guyana-budget-48614b0661ff.herokuapp.com/",
        label="Guyana Budget Analysis Page"
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.write(msg["content"])

        if msg["role"] == "assistant":

            if msg.get("sources"):

                with st.expander("Sources"):
                    
                    for source in msg["sources"]:

                        st.write(
                            #source[2]
                        )

#test = test_db()
#st.write("Test ", test)
question = st.chat_input(
    "Ask a question about the Guyana Constitution."
)

if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.write(question)

    with st.spinner(
        "Searching document..."
    ):

        result = answer_question(
            question
        )

    with st.chat_message(
        "assistant"
    ):

        st.write(
            result["answer"]
        )

        st.caption(
            f"Confidence: {result['score']:.2f}"
        )


    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"]
        }
    )