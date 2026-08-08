SYSTEM_PROMPT = """You are an enterprise knowledge assistant for Northwind Traders.
Answer only from the provided context. If the context does not contain enough evidence, say:
"I do not have enough information in the provided documents to answer that."

Rules:
- Be concise and specific.
- Write a clean natural-language answer.
- Do NOT include chunk IDs, bracket codes, or raw metadata in the answer.
- Sources are shown separately by the application.
- If a question is ambiguous, ask a clarification question instead of guessing.
- Prefer current/effective documents when versions conflict.
"""


def build_user_prompt(question: str, chunks: list[dict]) -> str:
    context_blocks = []
    for idx, chunk in enumerate(chunks, start=1):
        source_name = str(chunk["source_file"]).split("/")[-1]
        context_blocks.append(
            "\n".join(
                [
                    f"Source {idx}: {source_name}",
                    f"Department: {chunk.get('department')}",
                    f"Section: {chunk.get('section')}",
                    f"Page: {chunk.get('page')}",
                    "Paragraph:",
                    chunk["content"],
                ]
            )
        )
    return f"""Question:
{question}

Retrieved context:
{chr(10).join(context_blocks)}

Write a clean answer with no chunk IDs or bracket codes."""
