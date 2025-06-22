from tabulate import tabulate
import pandas as pd
import numpy as np
from typing import Dict, Any

def preprocess_table(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess and summarize large tables."""
    # Get non-NaN columns only
    valid_cols = df.columns[df.notna().any()].tolist()
    df = df[valid_cols]
    
    # Get numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    # Calculate summary statistics for numeric columns
    if len(numeric_cols) > 0:
        summary_stats = df[numeric_cols].agg(['mean', 'min', 'max']).round(2)
        df = pd.DataFrame(summary_stats)
    
    # Limit rows and columns for non-numeric data
    if len(df) > 10:
        df = df.head(10)
    if len(df.columns) > 8:
        df = df.iloc[:, :8]
        
    return df

def prompt_builder_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Build a prompt combining question text and table data."""
    question_id = state.get("question_id", "unknown")
    question_text = state.get("question_text", "")
    
    # Convert table_dict back to DataFrame if available
    table_df = None
    if "table_dict" in state:
        try:
            table_dict = state["table_dict"]
            table_df = pd.DataFrame(table_dict["data"], columns=table_dict["columns"])
            print(f"\nFull table shape: {table_df.shape}")
            
            # Preprocess table
            table_df = preprocess_table(table_df)
            print(f"Processed table shape: {table_df.shape}")
            
        except Exception as e:
            print(f"Error processing table data: {e}")
            return {
                **state,
                "prompt": f"Error processing table: {str(e)}"
            }

    if table_df is None:
        return {
            **state,
            "prompt": "No table data available for analysis"
        }

    try:
        # Convert DataFrame to list format for tabulate
        headers = table_df.columns.tolist()
        table_data = table_df.values.tolist()
        
        # Format table as markdown
        formatted_table = tabulate(
            table_data,
            headers=headers,
            tablefmt="github",
            showindex=True
        )

        # Build prompt
        prompt = f"""
You are an expert market research analyst analyzing OTT/video streaming app survey data.

Question ID: {question_id}

Question Text: 
{question_text}

Survey Response Data (showing key statistics):
{formatted_table}

Please provide:
1. Key Findings:
   - Top 3 clear and data-driven insights
   - Focus on usage patterns, preferences, and trends

2. Recommendations:
   - 2 actionable recommendations based on the findings
   - Consider business implications and opportunities

Format your response with clear sections and bullet points.
"""

        print("\nPrompt built successfully.")
        return {
            **state,
            "prompt": prompt
        }

    except Exception as e:
        print(f"Failed to build prompt: {e}")
        return {
            **state,
            "prompt": f"Failed to build prompt: {str(e)}"
        }

# Test the node
if __name__ == "__main__":
    test_state = {
        "question_id": "Q10.1",
        "question_text": "Which OTT apps do you use?",
        "table_dict": {
            "columns": ["App", "Usage"],
            "data": [["Netflix", 80], ["Prime", 60]]
        }
    }
    result = prompt_builder_node(test_state)
    print("\nTest Result:", result)
