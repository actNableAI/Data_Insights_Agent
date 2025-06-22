import sys
from typing import Dict, Any

def input_node() -> Dict[str, Any]:
    """Get question input from user."""
    # Set console encoding to UTF-8
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            # Python < 3.7
            pass

    try:
        # Simple prompt without emojis
        user_question = input("\nAsk a question related to the survey (e.g., 'What does Q10.1 ask?'):\n> ")
    except UnicodeEncodeError:
        # Fallback prompt without special characters
        user_question = input("\nEnter your question: ")

    return {
        "question": user_question.strip()
    }

# Test the node
if __name__ == "__main__":
    result = input_node()
    print("\nTest Result:", result)
