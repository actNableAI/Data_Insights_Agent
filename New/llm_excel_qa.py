import pandas as pd
from tabulate import tabulate
from openai import OpenAI
from utils import load_keys

def load_col_sheet(filepath: str, sheet_name: str = "col%") -> pd.DataFrame:
    xls = pd.ExcelFile(filepath)
    if sheet_name not in xls.sheet_names:
        raise ValueError(f"Sheet '{sheet_name}' not found in the file.")
    df = xls.parse(sheet_name, header=None)
    return df

def prepare_prompt(question: str, data_df: pd.DataFrame) -> str:
    # Take first 30 rows and 20 columns for now
    short_df = data_df.iloc[:30, :20].fillna("")
    formatted_table = tabulate(short_df, headers="keys", tablefmt="pipe", showindex=False)
    
    prompt = f"""
You are a data analyst looking at the following table from a market research Excel file.

The table contains responses from a survey related to OTT platform awareness, trust, and usage.

Here is a snippet of the data:

{formatted_table}

Now answer this question clearly:

Q: {question}
A:"""
    return prompt

def ask_question_to_llm(prompt: str):
    keys = load_keys()
    client = OpenAI(api_key=keys["OPENAI_API_KEY"])

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful market research data analyst."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content

# Entry point
if __name__ == "__main__":
    excel_path = r"Data\raw data\Tables.xlsx"
    question = "Which OTT app has the highest awareness?"

    df = load_col_sheet(excel_path)
    prompt = prepare_prompt(question, df)
    answer = ask_question_to_llm(prompt)

    print("\n🔍 GPT's Answer:")
    print(answer)
