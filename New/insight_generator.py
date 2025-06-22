import pandas as pd
from openai import OpenAI
from typing import Optional, Tuple
from utils import load_keys, extract_insights_and_recommendations
from table_extractor import TableExtractor
from prompt_builder import PromptBuilder
from pinecone_search import query_pinecone
from google_doc_saver import create_insight_doc

class InsightGenerator:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize InsightGenerator with optional API key."""
        if api_key is None:
            keys = load_keys()
            api_key = keys.get("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in .env file or pass it directly.")

        if not isinstance(api_key, str):
            raise ValueError("Invalid API key format - must be a string.")

        self.client = OpenAI(api_key=api_key)
        self.extractor = None
        self.prompt_builder = None

    def setup_project(self,
                      filepath: str,
                      brand_name: Optional[str] = None,
                      study_context: Optional[str] = None) -> None:
        """Set up the project with data file and context."""
        self.extractor = TableExtractor(filepath)
        self.extractor.load_excel()
        self.prompt_builder = PromptBuilder(brand_name, study_context)

    def generate_insights(self,
                          question_id: str,
                          num_insights: int = 3,
                          num_recommendations: int = 2) -> Tuple[str, str, str]:
        """
        Generate insights for a specific question.

        Args:
            question_id: The question ID (e.g., "Q10.1")
            num_insights: Number of insights to request
            num_recommendations: Number of recommendations to request

        Returns:
            Tuple[str, str, str]: (question_text, insights, google_doc_url)
        """
        if self.extractor is None or self.prompt_builder is None:
            raise ValueError("Project not set up. Call setup_project() first.")

        try:
            # Extract and clean the table data
            _, table_df = self.extractor.extract_question_table(question_id)

            # Try to get the real question text from Pinecone
            try:
                matches = query_pinecone(question_id)
                question_text = next((m for m in matches if question_id.lower() in m.lower()), matches[0])
                question_text = question_text.split("\nQ")[0].strip()
            except Exception:
                question_text = question_id

            # Filter good columns from the table
            all_columns = [col for col in table_df.columns if pd.notna(col)]
            relevant_columns = []
            key_terms = ['total', 'base', 'male', 'female', 'age', 'nccs', 'years']

            for col in all_columns:
                col_str = str(col).lower()
                if 'all' in col_str or any(term in col_str for term in key_terms):
                    relevant_columns.append(col)

            if len(relevant_columns) < 5:
                relevant_columns.extend(all_columns[:10])

            relevant_columns = list(dict.fromkeys(relevant_columns))[:10]
            trimmed_df = table_df[relevant_columns].copy()

            # Format the cleaned table
            formatted_df = self.extractor.format_table(trimmed_df)
            print("\n Formatted Table Preview:\n")
            print(formatted_df)

            # Build prompt
            prompt = self.prompt_builder.build_insight_prompt(
                question_text=question_text,
                table_df=formatted_df,
                base_size=2314,
                num_insights=num_insights,
                num_recommendations=num_recommendations
            )

            print("\nFinal Prompt Preview:\n")
            print(prompt)

            print(f"\nGenerating insights for {question_id}...")
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert market research analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            if not response.choices or not response.choices[0].message.content:
                raise RuntimeError("No response received from GPT")

            insights = response.choices[0].message.content
            if not isinstance(insights, str):
                raise RuntimeError("Invalid response format from GPT")

            # Extract trimmed content (Insights + Recommendations only)
            trimmed_output = extract_insights_and_recommendations(insights)

            # Save to Google Docs
            url = create_insight_doc(
                question_id=question_id,
                question_text=question_text,
                insights=trimmed_output
            )
            print(f"\nInsights saved to Google Doc: {url}")

            return question_text, trimmed_output, url

        except Exception as e:
            error_msg = f"Error generating insights for {question_id}: {str(e)}"
            print(f"\nERROR: {error_msg}")
            raise RuntimeError(error_msg)

def test_insight_generation():
    """Test the insight generation pipeline."""
    try:
        # Initialize the generator
        generator = InsightGenerator()

        # Set up the project
        generator.setup_project(
            filepath="Data/raw data/Tables.xlsx",
            brand_name="TestBrand",
            study_context="brand awareness study"
        )

        # Generate insights for a question
        question_text, insights, url = generator.generate_insights("Q10.1")

        # Print output
        print("\nQuestion:", question_text)
        print("\nInsights:\n=========")
        print(insights)
        print("\nInsights saved to:", url)

    except Exception as e:
        print(f"\nTest failed: {str(e)}")

if __name__ == "__main__":
    test_insight_generation()
