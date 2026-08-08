SYSTEM_PROMPT = """You are an enterprise knowledge assistant for Northwind Traders.
Answer only from the provided context. If the context does not contain enough evidence, say:
"I do not have enough information in the provided documents to answer that."

Rules:
- Be concise and specific.
- Include citations using bracketed chunk ids like [abc123].
- Do not cite a chunk unless it directly supports the claim.
- If a question is ambiguous, ask a clarification question instead of guessing.
- Prefer current/effective documents when versions conflict.
"""


def build_user_prompt(question: str, chunks: list[dict]) -> str:
    context_blocks = []
    for chunk in chunks:
        context_blocks.append(
            "\n".join(
                [
                    f"Chunk ID: {chunk['chunk_id']}",
                    f"Source: {chunk['source_file']}",
                    f"Department: {chunk.get('department')}",
                    f"Section: {chunk.get('section')}",
                    f"Page: {chunk.get('page')}",
                    f"Version: {chunk.get('version')}",
                    f"Effective Date: {chunk.get('effective_date')}",
                    f"Current: {chunk.get('is_current')}",
                    "Content:",
                    chunk["content"],
                ]
            )
        )
    return f"""Question:
{question}

Retrieved context:
{chr(10).join(context_blocks)}

Answer with citations."""
