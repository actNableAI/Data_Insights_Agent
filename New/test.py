from insight_generator import InsightGenerator

# Create a minimal logger to show prompt being sent to GPT
def test_input_verification():
    generator = InsightGenerator()
    generator.setup_project(
        filepath="Data/raw data/Tables.xlsx",
        brand_name="SonyLiv",
        study_context="OTT platform usage & brand preference"
    )

    question_id = "Q10.1"
    question_text, insights, _ = generator.generate_insights(question_id)

    print("\n✅ Final Question Text from PDF:")
    print(question_text)

    print("\n✅ Insights Generated:")
    print(insights)

if __name__ == "__main__":
    test_input_verification()
