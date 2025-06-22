from utils import load_keys
from table_extractor import TableExtractor
from prompt_builder import PromptBuilder
from pinecone_search import query_pinecone

def preview_prompt_for_question(question_id: str):
    # Load keys and setup
    keys = load_keys()
    filepath = "Data/raw data/Tables.xlsx"
    brand_name = "SonyLiv"
    study_context = "OTT usage and brand perception survey"

    # Set up data extractor and prompt builder
    extractor = TableExtractor(filepath)
    extractor.load_excel()
    prompt_builder = PromptBuilder(brand_name, study_context)

    # Load question text from Pinecone (PDF)
    try:
        matches = query_pinecone(question_id)
        question_text = next((m for m in matches if question_id.lower() in m.lower()), matches[0])
    except Exception:
        question_text = question_id

    # Load table for the question from Excel
    _, table_df = extractor.extract_question_table(question_id)
    all_columns = [col for col in table_df.columns if col]
    trimmed_df = table_df[all_columns[:10]].copy()
    formatted_table = extractor.format_table(trimmed_df)

    #  Build the prompt
    prompt = prompt_builder.build_insight_prompt(
        question_text=question_text,
        table_df=formatted_table,
        base_size=2314,
        num_insights=3,
        num_recommendations=2
    )

    # Print everything
    print(f"\n\n=== QUESTION TEXT from Pinecone ===\n{question_text}\n")
    print(f"=== FORMATTED TABLE from Excel ===\n{formatted_table}\n")
    print(f"=== FINAL PROMPT SENT TO GPT ===\n{prompt}\n")

if __name__ == "__main__":
    preview_prompt_for_question("Q10.1")
