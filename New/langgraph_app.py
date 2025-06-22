from langgraph.graph import StateGraph, END
from input_node import input_node 
from pdf_query_node import query_pdf_question_node
from table_extractor_node import table_extractor_node
from prompt_builder_node import prompt_builder_node
from insight_gpt_node import insight_gpt_node
from save_to_doc_node import save_to_doc_node
from output_node import output_node
from typing import TypedDict, List, Dict, Any
import pandas as pd

# Define the keys we'll pass between nodes
class WorkflowState(TypedDict):
    question: str
    question_id: str
    question_text: str
    table_dict: Dict[str, Any]
    table_shape: tuple
    prompt: str
    insights: str
    doc_url: str

# Create the graph
rag_graph = StateGraph(WorkflowState)

# Add nodes (functions)
rag_graph.add_node("query_pdf", query_pdf_question_node)
rag_graph.add_node("extract_table", table_extractor_node)
rag_graph.add_node("build_prompt", prompt_builder_node)
rag_graph.add_node("generate_insights", insight_gpt_node)
rag_graph.add_node("save_to_doc", save_to_doc_node)
rag_graph.add_node("output", output_node)

# Define edges between nodes (order of execution)
rag_graph.set_entry_point("query_pdf")
rag_graph.add_edge("query_pdf", "extract_table")
rag_graph.add_edge("extract_table", "build_prompt")
rag_graph.add_edge("build_prompt", "generate_insights")
rag_graph.add_edge("generate_insights", "save_to_doc")
rag_graph.add_edge("save_to_doc", "output")
rag_graph.set_finish_point("output")

# Compile into a runnable app
app = rag_graph.compile()

# Test the full pipeline
if __name__ == "__main__":
    # Get user question via input node
    initial_state = input_node()

    # Run the LangGraph pipeline
    final_state = app.invoke(initial_state)

    print("\nFull pipeline completed!")
    print("Final Output State:")
    for k, v in final_state.items():
        if k == "table_dict":
            print(f"{k}: [DataFrame with shape {final_state.get('table_shape', 'unknown')}]")
        else:
            print(f"{k}: {v}")
