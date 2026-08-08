import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000/chat")

st.set_page_config(page_title="Northwind Knowledge Assistant", layout="wide")
st.title("Northwind Knowledge Assistant")

with st.sidebar:
    st.subheader("Retrieval")
    improved = st.toggle("Improved RAG", value=True)
    department = st.selectbox("Department filter", ["", "HR", "Finance", "IT", "Legal", "Sales"])
    groups = st.multiselect("Access groups", ["HR", "Finance", "IT", "Legal", "Sales"], default=["HR", "Finance", "IT", "Legal", "Sales"])
    top_k = st.slider("Top K", 3, 10, 6)

question = st.chat_input("Ask about leave, pricing, expenses, VPN, contracts, benefits...")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    payload = {
        "question": question,
        "department": department or None,
        "access_groups": groups,
        "history": st.session_state.messages[-6:],
        "improved": improved,
        "top_k": top_k,
    }
    with st.chat_message("assistant"):
        with st.spinner("Retrieving evidence..."):
            response = requests.post(API_URL, json=payload, timeout=90)
        if response.ok:
            data = response.json()
            st.markdown(data["answer"])
            with st.expander("Evidence"):
                st.json({
                    "confidence": data["confidence"],
                    "latency_ms": data["latency_ms"],
                    "rewritten_query": data["rewritten_query"],
                    "citations": data["citations"],
                    "retrieved_chunks": data["retrieved_chunks"],
                })
            st.session_state.messages.append({"role": "assistant", "content": data["answer"]})
        else:
            st.error(response.text)
