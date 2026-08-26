import streamlit as st

from support.core.chatbot import get_groq_api_key, get_response
from support.core.data import get_prepared_dataset
from support.core.theme import apply_theme, error_state, page_header

apply_theme("Chat Assistant")

st.markdown(
    """
    <style>
    [data-testid="stBottomBlockContainer"],
    [data-testid="stBottomBlockContainer"] .block-container {
        max-width: 100% !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
    }
    [data-testid="stChatInput"] {
        max-width: 100% !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

page_header(
    "Chat Assistant",
    "Ask it anything about the food data",
    "Quick facts like calories, condition fit, recipes, and meal plans answer instantly from the dataset. "
    "Anything else goes to Groq, grounded in the same data.",
)

dataset = get_prepared_dataset()
if dataset.empty:
    error_state("Dataset not found", "Add <code>bd_food_nutrition_dataset.csv</code> to the project root.")
    st.stop()

if not get_groq_api_key():
    st.caption("Groq API key not configured. Open-ended questions will fall back to a dataset-only answer.")

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": "Ask me about calories, whether a food fits a condition, a recipe, or a meal plan. "
            "I'll answer straight from the dataset, or Groq if it's an open-ended question.",
        }
    ]

for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("note"):
            st.caption(message["note"])

user_input = st.chat_input("Ask about a food, a diet, a recipe, or a meal plan…")

if user_input:
    st.session_state.chat_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    history = [
        {"role": message["role"], "content": message["content"]}
        for message in st.session_state.chat_messages
        if message["role"] in ("user", "assistant")
    ][-10:]

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            reply, note = get_response(user_input, history, dataset)
        st.markdown(reply)
        if note:
            st.caption(note)

    st.session_state.chat_messages.append({"role": "assistant", "content": reply, "note": note})
