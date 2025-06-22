import pandas as pd
import os

class TableExtractor:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.excel = None
        self.sheet_name = "col%"  # Default sheet name

    def load_excel(self, sheet_name: str = None):
        """Load the Excel file and optionally override the default sheet name."""
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"File not found: {self.filepath}")

        self.excel = pd.ExcelFile(self.filepath)
        print(f" Excel file loaded: {self.filepath}")
        print(" Sheets available:", self.excel.sheet_names)

        if sheet_name:
            if sheet_name not in self.excel.sheet_names:
                raise ValueError(f"Sheet '{sheet_name}' not found in Excel file.")
            self.sheet_name = sheet_name  # Override default

    def extract_question_table(self, question_id: str, window_size: int = 25) -> tuple:
        """
        Extract a block of rows under a specific question ID (like Q10.1).
        Returns (question_text, DataFrame)
        """
        if self.excel is None:
            raise ValueError("Excel file not loaded. Call load_excel() first.")

        df = self.excel.parse(self.sheet_name, header=None)
        print(f"\n Searching for question ID: {question_id} in sheet '{self.sheet_name}'...")

        # Find the row containing the question ID
        start_row = None
        for i in range(len(df)):
            row_text = " ".join(str(cell) for cell in df.iloc[i].values if pd.notna(cell)).lower()
            if question_id.lower() in row_text:
                start_row = i
                break

        if start_row is None:
            raise ValueError(f" Question ID '{question_id}' not found in sheet '{self.sheet_name}'.")

        print(f" Found question at row {start_row}:  {row_text[:100]}...")

        # Extract a window of rows under the question
        table_data = df.iloc[start_row + 1 : start_row + 1 + window_size]

        # Promote first row to header
        table_data.columns = table_data.iloc[0]
        table_data = table_data.drop(table_data.index[0])
        table_data = table_data.reset_index(drop=True)

        print(f" Extracted table with shape: {table_data.shape} (rows x columns)")
        return row_text.strip(), table_data

    def format_table(self, df: pd.DataFrame) -> str:
        """Format table to markdown for GPT."""
        df = df.copy()
        for col in df.columns:
            try:
                df[col] = df[col].apply(lambda x: f"{x:.1f}%" if pd.notna(x) and isinstance(x, (float, int)) else x)
            except Exception:
                continue

        try:
            return df.to_markdown(index=False)
        except Exception as e:
            return f"**Table formatting failed: {str(e)}**"


