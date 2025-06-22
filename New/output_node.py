def output_node(state):
    """Final LangGraph node that displays the results."""
    print("\nFinal Output Summary")
    print("=========================")

    question_id = state.get("question_id", "N/A")
    question_text = state.get("question_text", "N/A")
    insights = state.get("insights", "No insights generated")
    doc_url = state.get("doc_url", "Not saved to Docs")

    print(f"\nQuestion ID: {question_id}")
    print(f"\nQuestion Text:\n{question_text}")
    print(f"\nInsights & Recommendations:\n{insights}")
    print(f"\nSaved to Google Docs: {doc_url}")

    # Return unchanged state (could be used for logging or further export)
    return state
