from dotenv import load_dotenv
import os
import re

def load_keys():
    load_dotenv()
    return {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "PINECONE_API_KEY": os.getenv("PINECONE_API_KEY"),
        "PINECONE_ENV": os.getenv("PINECONE_ENVIRONMENT"),
        "PINECONE_INDEX": os.getenv("PINECONE_INDEX_NAME")
    }

import re

def extract_insights_and_recommendations(text: str) -> str:
    try:
        # Look for first numbered list and split after about 3 points
        sections = re.findall(r"(?:\d\..*?)(?=(?:\n\d\.|\Z))", text, re.DOTALL)

        if len(sections) >= 5:
            insights = "\n".join(sections[:3])
            recommendations = "\n".join(sections[3:5])
            return f"**Insights:**\n\n{insights}\n\n\n\n{recommendations}"
        else:
            return f"**Raw Output:**\n\n{text.strip()[:1000]}"

    except Exception as e:
        return f"⚠️ Error extracting insights: {str(e)}"

