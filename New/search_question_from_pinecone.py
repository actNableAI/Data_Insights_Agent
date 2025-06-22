from pinecone_search import query_pinecone

def get_clean_question_text(self, question_id: str, top_k: int = 5) -> str:
    matches = query_pinecone(question_id, top_k=top_k)

    for match in matches:
        lines = match.strip().splitlines()
        for i, line in enumerate(lines):
            if line.strip().lower().startswith(question_id.lower()):
                # Include next 2–3 lines for context (you can increase this if needed)
                context_lines = lines[i:i+5]
                return " ".join(line.strip() for line in context_lines if line.strip())

    # fallback
    for match in matches:
        if question_id.lower() in match.lower():
            return match.strip()

    return question_id

if __name__ == "__main__":
    question_id = "Q11.1"
    result = get_clean_question_text(question_id)
    print(f"\nCleaned Question Output:\n{result}")
