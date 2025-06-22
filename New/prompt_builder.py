class PromptBuilder:
    def __init__(self, brand_name=None, study_context=None):
        self.brand_name = brand_name or "the brand"
        self.study_context = study_context or "a general market research study"

    def build_insight_prompt(self, question_text: str, table_df: str, base_size: int = 1000, num_insights: int = 3, num_recommendations: int = 2) -> str:
        """
        Build a basic prompt to send to GPT.
        Args:
            question_text: Actual question being analyzed
            table_df: Cleaned table in markdown format
            base_size: Total number of respondents
            num_insights: How many insights to ask for
            num_recommendations: How many action points to ask for
        Returns:
            Full prompt string
        """
        prompt = f"""
You are an expert market research analyst.

This data is from a survey about {self.brand_name}. The study focuses on {self.study_context}.

Below is the question and the response data table:

**Question:**
{question_text}

**Base size:** {base_size} respondents

**Data Table:**
{table_df}

Please generate {num_insights} clear, concise insights from this data.
Then provide {num_recommendations} actionable recommendations based on the insights.
"""
        return prompt
