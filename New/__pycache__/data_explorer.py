# data_explorer.py

import pandas as pd
import os

def explore_excel(file_path: str):
    """Load an Excel file and list its sheet names."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    xls = pd.ExcelFile(file_path)
    print(f"\n📂 Loading Excel file: {file_path}")
    print("📄 Sheets found:", xls.sheet_names)
    return xls

def read_sheet(xls: pd.ExcelFile, sheet_name: str, show_rows: int = 10):
    """Read a specific sheet and preview its content."""
    try:
        df = xls.parse(sheet_name)
        print(f"\n📑 Sheet: {sheet_name}")
        print(df.head(show_rows))
        print(f"\n✅ Data shape: {df.shape} (rows, columns)")
        return df
    except ValueError:
        raise ValueError(f"Sheet '{sheet_name}' not found in Excel file.")

if __name__ == "__main__":
    excel_path = r"Data\raw data\Tables.xlsx"  # Change to your actual file path
    xls = explore_excel(excel_path)

    # Example: preview the 'col%' sheet
    sheet_name = "col%"
    df = read_sheet(xls, sheet_name)

    # Optional: Show column names
    print("\n📊 Columns detected:")
    for col in df.columns:
        print(" -", col)
