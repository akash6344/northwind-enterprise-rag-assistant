import os
from pathlib import Path

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000/chat")

st.set_page_config(
    page_title="Northwind Knowledge Assistant",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": None,
        "Report a bug": None,
        "About": None,
    },
)

HIDE_CHROME = """
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,600&display=swap');
#MainMenu, footer {visibility: hidden;}
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
.stDeployButton,
[data-testid="stAppDeployButton"],
#stDecoration {display: none !important;}
[data-testid="stHeader"] {
  background: transparent !important;
  height: 0 !important;
  min-height: 0 !important;
}
[data-testid="collapsedControl"] {
  visibility: visible !important;
  display: flex !important;
  color: var(--nw-text) !important;
}
"""

NIGHT_THEME = """
:root {
  --nw-bg: #0b0b0c;
  --nw-bg-2: #141416;
  --nw-surface: #1a1a1d;
  --nw-text: #f4f1ea;
  --nw-muted: #a39e93;
  --nw-border: #2c2c31;
  --nw-orange: #ff6a00;
  --nw-orange-soft: rgba(255, 106, 0, 0.16);
  --nw-sidebar: #101012;
  --nw-input: #17171a;
  --nw-chip: #22180f;
  --nw-stripe: linear-gradient(90deg, #ff6a00 0%, #ff8a2b 45%, #ff6a00 100%);
}
"""

LIGHT_THEME = """
:root {
  --nw-bg: #f6f3ee;
  --nw-bg-2: #fffdf9;
  --nw-surface: #ffffff;
  --nw-text: #171717;
  --nw-muted: #6f675c;
  --nw-border: #e4ddd2;
  --nw-orange: #e85d04;
  --nw-orange-soft: rgba(232, 93, 4, 0.12);
  --nw-sidebar: #fff8f1;
  --nw-input: #ffffff;
  --nw-chip: #fff1e4;
  --nw-stripe: linear-gradient(90deg, #e85d04 0%, #ff8a2b 45%, #e85d04 100%);
}
"""

APP_CSS = """
html, body, [class*="css"] {
  font-family: 'Outfit', sans-serif !important;
}
.stApp, [data-testid="stAppViewContainer"] {
  background:
    radial-gradient(1200px 500px at 10% -10%, rgba(255,106,0,0.12), transparent 55%),
    var(--nw-bg) !important;
  color: var(--nw-text) !important;
}
.nw-top-stripe {
  height: 6px;
  width: 100%;
  background: var(--nw-stripe);
  border-radius: 999px;
  margin: 0.2rem 0 1rem 0;
  box-shadow: 0 0 18px rgba(255, 106, 0, 0.35);
}
.nw-brand {
  font-family: 'Source Serif 4', serif !important;
  font-size: 2.1rem !important;
  font-weight: 600 !important;
  letter-spacing: -0.02em;
  margin: 0 !important;
  color: var(--nw-text) !important;
}
.nw-brand span {
  color: var(--nw-orange);
}
.nw-subtitle {
  color: var(--nw-muted);
  margin: 0.15rem 0 1.1rem 0;
  font-size: 0.95rem;
}
[data-testid="stSidebar"] > div:first-child {
  background: var(--nw-sidebar) !important;
  border-right: 1px solid var(--nw-border) !important;
}
[data-testid="stSidebar"]::before {
  content: "";
  display: block;
  height: 4px;
  background: var(--nw-stripe);
}
[data-testid="stChatMessage"] {
  background: var(--nw-surface) !important;
  border: 1px solid var(--nw-border) !important;
  border-left: 3px solid var(--nw-orange) !important;
  border-radius: 14px !important;
}
[data-testid="stExpander"] {
  background: var(--nw-bg-2) !important;
  border: 1px solid var(--nw-border) !important;
  border-radius: 12px !important;
}
[data-testid="stChatInput"] textarea {
  background: var(--nw-input) !important;
  color: var(--nw-text) !important;
  border: 1px solid var(--nw-border) !important;
  border-radius: 14px !important;
}
.stCaption, [data-testid="stCaptionContainer"] {
  color: var(--nw-muted) !important;
}
hr { border-color: var(--nw-border) !important; }
.nw-source-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin: 0 0 0.85rem 0;
}
.nw-source-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: var(--nw-chip);
  color: var(--nw-text);
  border: 1px solid color-mix(in srgb, var(--nw-orange) 45%, var(--nw-border));
  border-radius: 999px;
  padding: 0.3rem 0.75rem;
  font-size: 0.82rem;
  line-height: 1.2;
}
.nw-source-chip strong { color: var(--nw-orange); }
.nw-source-chip span {
  color: var(--nw-muted);
  font-size: 0.75rem;
}
.nw-answer-label {
  color: var(--nw-orange);
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin: 0.45rem 0 0.35rem 0;
  font-weight: 600;
}
div[data-testid="stRadio"] label {
  color: var(--nw-text) !important;
}
"""


def apply_theme(mode: str) -> None:
    palette = NIGHT_THEME if mode == "Night" else LIGHT_THEME
    st.markdown(f"<style>{HIDE_CHROME}{palette}{APP_CSS}</style>", unsafe_allow_html=True)


def evidence_items(data: dict) -> list[dict]:
    citations = data.get("citations") or []
    chunks = data.get("retrieved_chunks") or []
    if not citations and not chunks:
        return []
    cited_ids = {item.get("chunk_id") for item in citations}
    items = [chunk for chunk in chunks if chunk.get("chunk_id") in cited_ids] if cited_ids else chunks
    return items or chunks


def render_sources(data: dict) -> None:
    items = evidence_items(data)
    if not items:
        return

    with st.expander(f"Sources ({len(items)})", expanded=False):
        chips = []
        for idx, chunk in enumerate(items, start=1):
            source = Path(chunk.get("source_file", "Unknown")).name
            section = chunk.get("section") or "General"
            chips.append(
                f'<div class="nw-source-chip"><strong>{idx}. {source}</strong><span>{section}</span></div>'
            )
        st.markdown(f'<div class="nw-source-row">{"".join(chips)}</div>', unsafe_allow_html=True)

        for idx, chunk in enumerate(items, start=1):
            source = Path(chunk.get("source_file", "Unknown")).name
            section = chunk.get("section") or "General"
            page = chunk.get("page")
            header = f"{idx}. {source} · {section}"
            if page is not None:
                header += f" · p.{page}"
            st.markdown(f"**{header}**")
            st.write(chunk.get("preview") or chunk.get("content") or "")
            if idx < len(items):
                st.divider()


def render_assistant(content: str, evidence: dict | None) -> None:
    with st.chat_message("assistant"):
        st.markdown(content)
        if evidence and (evidence.get("citations") or evidence.get("retrieved_chunks")):
            render_sources(evidence)


if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Night"

with st.sidebar:
    st.markdown("### Theme")
    theme_mode = st.radio(
        "Theme",
        ["Night", "Light"],
        index=0 if st.session_state.theme_mode == "Night" else 1,
        horizontal=True,
        label_visibility="collapsed",
        help="Night = black + orange stripe. Light = warm paper + orange accent.",
    )
    st.session_state.theme_mode = theme_mode
    apply_theme(theme_mode)

    st.markdown("### Retrieval")
    improved = st.toggle("Improved RAG", value=True)
    department = st.selectbox("Department filter", ["", "HR", "Finance", "IT", "Legal", "Sales"])
    groups = st.multiselect(
        "Access groups",
        ["HR", "Finance", "IT", "Legal", "Sales"],
        default=["HR", "Finance", "IT", "Legal", "Sales"],
    )
    top_k = st.slider("Top K", 3, 10, 6)

st.markdown('<div class="nw-top-stripe"></div>', unsafe_allow_html=True)
st.markdown(
    '<p class="nw-brand">Northwind <span>Knowledge</span> Assistant</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="nw-subtitle">Grounded enterprise answers with citations from HR, Finance, IT, Legal, and Sales.</p>',
    unsafe_allow_html=True,
)

question = st.chat_input("Ask about leave, pricing, expenses, VPN, contracts, benefits...")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        render_assistant(msg["content"], msg.get("evidence"))

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    payload = {
        "question": question,
        "department": department or None,
        "access_groups": groups,
        "history": [
            {"role": item["role"], "content": item["content"]}
            for item in st.session_state.messages[-6:]
        ],
        "improved": improved,
        "top_k": top_k,
    }

    with st.spinner("Retrieving evidence..."):
        response = requests.post(API_URL, json=payload, timeout=90)

    if response.ok:
        data = response.json()
        evidence = {
            "citations": data.get("citations", []),
            "retrieved_chunks": data.get("retrieved_chunks", []),
        }
        has_sources = bool(evidence["citations"] or evidence["retrieved_chunks"])
        show_evidence = evidence if has_sources and not data.get("insufficient_evidence") else None
        render_assistant(data["answer"], show_evidence)
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": data["answer"],
                "evidence": show_evidence,
            }
        )
    else:
        with st.chat_message("assistant"):
            st.error(response.text)
