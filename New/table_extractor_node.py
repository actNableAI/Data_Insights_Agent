from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import re

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize column names."""
    df.columns = [str(col).strip().lower() for col in df.columns]
    # Remove special characters but keep spaces
    df.columns = [re.sub(r'[^\w\s]', '', col) for col in df.columns]
    return df

def extract_relevant_columns(df: pd.DataFrame, question: str) -> pd.DataFrame:
    """Extract columns relevant to the question."""
    # Basic columns to always include
    base_cols = ['base', 'all', 'total', 'unweighted']
    demo_cols = ['age', 'gender', 'nccs', 'sec', 'town', 'city', 'zone']
    
    # Get question-specific columns
    keywords = []
    if 'netflix' in question.lower():
        keywords.extend(['netflix', 'ott', 'streaming'])
    elif 'prime' in question.lower():
        keywords.extend(['prime', 'amazon', 'ott'])
    elif 'hotstar' in question.lower():
        keywords.extend(['hotstar', 'disney', 'ott'])
    else:
        keywords.extend(['ott', 'app', 'platform', 'streaming'])

    # Find relevant columns
    relevant_cols = []
    for col in df.columns:
        col_lower = str(col).lower()
        if (any(base in col_lower for base in base_cols) or
            any(demo in col_lower for demo in demo_cols) or
            any(key in col_lower for key in keywords)):
            relevant_cols.append(col)
            
    return df[relevant_cols] if relevant_cols else df

def clean_numeric_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and convert numeric data."""
    # Convert percentage strings to floats
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(lambda x: 
                float(str(x).replace('%', '')) if isinstance(x, str) 
                and '%' in x and str(x).replace('%', '').replace('.', '').isdigit()
                else x
            )
    return df

def summarize_app_data(df: pd.DataFrame, app_name: str) -> Dict[str, Any]:
    """Generate summary statistics for specific app."""
    app_cols = [col for col in df.columns if app_name.lower() in str(col).lower()]
    if not app_cols:
        return {}
        
    app_data = df[app_cols]
    numeric_cols = app_data.select_dtypes(include=[np.number]).columns
    
    summary = {
        "total_users": app_data[numeric_cols].mean().mean(),
        "by_age_group": {},
        "by_gender": {},
        "by_region": {}
    }
    
    # Extract demographic breakdowns if available
    age_cols = [col for col in df.columns if 'age' in str(col).lower()]
    gender_cols = [col for col in df.columns if 'gender' in str(col).lower()]
    region_cols = [col for col in df.columns if any(x in str(col).lower() for x in ['zone', 'region', 'city'])]
    
    if age_cols:
        summary["by_age_group"] = df[age_cols].mean().to_dict()
    if gender_cols:
        summary["by_gender"] = df[gender_cols].mean().to_dict()
    if region_cols:
        summary["by_region"] = df[region_cols].mean().to_dict()
        
    return summary

def table_extractor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Extract and process table data based on question context."""
    question_id = state.get("question_id", "unknown")
    question_text = state.get("question", "")
    
    print(f"\nExtracting table for Question ID: {question_id}")
    
    try:
        # Load Excel file
        excel_path = "Data/raw data/Tables.xlsx"
        print(f"Excel file loaded: {excel_path}")
        
        xlsx = pd.ExcelFile(excel_path)
        sheets = xlsx.sheet_names
        print(f"Sheets available: {sheets}")
        
        # Search in col% sheet
        sheet = "col%"
        df = pd.read_excel(excel_path, sheet_name=sheet)
        
        print(f"\nSearching for question ID: {question_id} in sheet '{sheet}'...")
        
        # Find rows containing question ID
        question_rows = df[df.astype(str).apply(lambda x: x.str.contains(question_id, case=False, na=False)).any(axis=1)]
        
        if len(question_rows) > 0:
            start_idx = question_rows.index[0]
            print(f" Found question at row {start_idx}: {df.iloc[start_idx, 0]}")
            
            # Extract table data (20 rows after question)
            table_df = df.iloc[start_idx:start_idx+20].copy()
            
            # Clean and process table
            table_df = clean_column_names(table_df)
            table_df = clean_numeric_data(table_df)
            table_df = extract_relevant_columns(table_df, question_text)
            
            print(f" Extracted table with shape: {table_df.shape}")
            
            # Create basic table dictionary
            table_dict = {
                "columns": table_df.columns.tolist(),
                "data": table_df.values.tolist(),
                "shape": table_df.shape
            }
            
            # Add app-specific summaries if relevant
            for app in ['netflix', 'prime', 'hotstar', 'youtube']:
                if app in question_text.lower():
                    summary = summarize_app_data(table_df, app)
                    if summary:
                        table_dict[f"{app}_summary"] = summary
            
            print(f"Processed table for {question_id}")
            
            return {
                **state,
                "table_dict": table_dict,
                "table_shape": table_df.shape
            }
            
        else:
            error_msg = f" Question ID '{question_id}' not found in sheet '{sheet}'."
            print(error_msg)
            raise ValueError(error_msg)
            
    except Exception as e:
        error_msg = f"Failed to extract table for {question_id}: {str(e)}"
        print(error_msg)
        return {
            **state,
            "error": error_msg
        }

# Test the node
if __name__ == "__main__":
    test_state = {
        "question": "What percentage of people use Netflix for watching movies?",
        "question_id": "Q11.3",
        "question_text": "Which OTT apps do you use?"
    }
    result = table_extractor_node(test_state)
    print("\nTest Result:")
    print(f"Table shape: {result.get('table_shape')}")
    if 'netflix_summary' in result.get('table_dict', {}):
        print("\nNetflix Summary:", result['table_dict']['netflix_summary'])
