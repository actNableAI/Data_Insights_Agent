from google_doc_saver import create_insight_doc

def save_to_doc_node(state):
    """LangGraph node that saves insights to Google Docs."""
    question_id = state.get("question_id", "unknown")
    question_text = state.get("question_text", "No question text provided")
    insights = state.get("insights", "No insights generated")

    print(f"\nSaving insights to Google Doc for {question_id}...")

    try:
        doc_url = create_insight_doc(
            question_id=question_id,
            question_text=question_text,
            insights=insights
        )
        print(f"Google Doc created: {doc_url}")

        return {
            **state,
            "doc_url": doc_url
        }

    except Exception as e:
        print(f"Failed to save Google Doc: {e}")
        return {
            **state,
            "doc_url": None,
            "error": str(e)
        }