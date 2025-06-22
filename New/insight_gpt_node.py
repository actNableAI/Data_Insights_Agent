from openai import OpenAI
from utils import load_keys
import pandas as pd
from typing import Dict, Any

def insight_gpt_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate insights using GPT-4."""
    question_id = state.get("question_id", "unknown")
    question_text = state.get("question_text", "")
    prompt = state.get("prompt", "")
    
    # Convert table_dict back to DataFrame if available
    table_df = None
    if "table_dict" in state:
        try:
            table_dict = state["table_dict"]
            table_df = pd.DataFrame(table_dict["data"], columns=table_dict["columns"])
            print(f"\nLoaded table with shape: {table_df.shape}")
        except Exception as e:
            print(f"Error converting table_dict to DataFrame: {e}")
            return {
                **state,
                "insights": f"Error processing table data: {str(e)}"
            }

    if not table_df is not None:
        print("No table data available")
        return {
            **state,
            "insights": "No table data available for analysis"
        }

    print(f"\nGenerating insights for {question_id}...")

    try:
        # Load API key
        keys = load_keys()
        client = OpenAI(api_key=keys["OPENAI_API_KEY"])

        # Send prompt to GPT-4
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert market research analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        # Safely extract content from response
        if (response and 
            hasattr(response, 'choices') and 
            response.choices and 
            hasattr(response.choices[0], 'message') and 
            response.choices[0].message and 
            hasattr(response.choices[0].message, 'content')):
            
            insights = response.choices[0].message.content
            if insights:
                insights = insights.strip()
            else:
                insights = "No insights generated from GPT"
        else:
            insights = "Error: Invalid response format from GPT"

        print("\nInsights generated:\n", insights)

        return {
            **state,
            "insights": insights
        }

    except Exception as e:
        error_msg = str(e)
        print("GPT Insight generation failed:", error_msg)
        return {
            **state,
            "insights": f"GPT failed: {error_msg}"
        }

# Test the node
if __name__ == "__main__":
    test_state = {
        "question_id": "Q10.1",
        "question_text": "Which OTT apps do you use?",
        "prompt": "Test prompt",
        "table_dict": {
            "columns": ["App", "Usage"],
            "data": [["Netflix", "80%"], ["Prime", "60%"]]
        }
    }
    result = insight_gpt_node(test_state)
    print("\nTest Result:", result)
