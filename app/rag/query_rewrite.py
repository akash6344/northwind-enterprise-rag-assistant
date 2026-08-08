AMBIGUOUS_TERMS = {"limit", "policy", "approval", "exception", "exceptions", "renewal", "cost", "approves"}


def is_ambiguous(question: str, history: list[dict[str, str]] | None = None) -> bool:
    if history:
        return False
    words = {word.strip("?.!,").lower() for word in question.split()}
    if len(words) <= 6 and words.intersection(AMBIGUOUS_TERMS):
        return True
    return False


def rewrite_query(question: str, history: list[dict[str, str]] | None = None) -> str:
    if not history:
        return question
    recent = " ".join(
        item.get("content", "")
        for item in history[-4:]
        if item.get("role") in {"user", "assistant"}
    )
    lower = question.lower().strip()
    if lower.startswith(("what about", "and ", "does it", "is there", "what is the", "does the older")):
        return (
            f"Using the conversation topic ({recent}), answer this follow-up as a "
            f"standalone enterprise knowledge-base question: {question}"
        )
    return question
