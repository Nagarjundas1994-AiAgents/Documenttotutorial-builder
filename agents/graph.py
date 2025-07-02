import os
from typing import TypedDict, List, Dict, Annotated
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langgraph.graph import StateGraph, END
from langchain_deepseek import ChatDeepSeek
import json

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Define the state for our graph
class GraphState(TypedDict):
    original_query: str
    scraped_content: str
    tutorial_outline: Dict
    section_drafts: Dict[str, str]
    final_tutorial: str
    error_message: str
    current_section_key: str

# Initialize the LLM
# llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0.2)
llm = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0,
    max_tokens=None
)


# --- AGENT NODES ---

def generate_outline(state: GraphState) -> GraphState:
    """Generates a structured outline for the tutorial."""
    print("---AGENT: Generating Outline---")
    prompt = ChatPromptTemplate.from_template(
        """Based on the following documentation content, create a logical, beginner-friendly tutorial outline.
        The output should be a JSON object with a 'title' for the whole tutorial and a list of 'sections', where each section has a 'title' and a 'brief_description'.

        Documentation Content:
        ---
        {content}
        ---
        User's original request: {query}
        
        JSON Output:"""
    )
    
    chain = prompt | llm | JsonOutputParser()
    
    try:
        outline = chain.invoke({
            "content": state['scraped_content'][:20000], # Use a subset to avoid token limits
            "query": state['original_query']
        })
        return {
            "original_query": state["original_query"],
            "scraped_content": state["scraped_content"],
            "tutorial_outline": outline,
            "section_drafts": {},
            "final_tutorial": "",
            "error_message": "",
            "current_section_key": "0"
        }
    except Exception as e:
        return {
            "original_query": state["original_query"],
            "scraped_content": state["scraped_content"],
            "tutorial_outline": {},
            "section_drafts": {},
            "final_tutorial": "",
            "error_message": f"Outline generation failed: {e}",
            "current_section_key": "0"
        }

def write_section(state: GraphState) -> GraphState:
    """Writes the content for a single section of the tutorial."""
    print(f"---AGENT: Writing Section: {state['current_section_key']}---")
    section_info = state['tutorial_outline']['sections'][int(state['current_section_key'])]
    prompt = ChatPromptTemplate.from_template(
        """You are an expert technical writer creating a tutorial.
        Your task is to write a detailed, clear, and beginner-friendly tutorial section.
        Use the provided documentation content as your primary source of truth.
        Include code examples where relevant, formatted in Markdown.
        Add analogies if they help explain complex topics.

        Full Documentation Context:
        ---
        {context}
        ---
        
        Tutorial Outline: {outline}

        Write the content for this section:
        - Section Title: {section_title}
        - Section Description: {section_description}

        Generate only the Markdown content for this specific section.
        """
    )
    chain = prompt | llm | StrOutputParser()
    section_content = chain.invoke({
        "context": state['scraped_content'],
        "outline": json.dumps(state['tutorial_outline']),
        "section_title": section_info['title'],
        "section_description": section_info['brief_description']
    })
    current_drafts = dict(state['section_drafts'])
    current_drafts[state['current_section_key']] = section_content
    return {
        "original_query": state["original_query"],
        "scraped_content": state["scraped_content"],
        "tutorial_outline": state["tutorial_outline"],
        "section_drafts": current_drafts,
        "final_tutorial": state["final_tutorial"],
        "error_message": state["error_message"],
        "current_section_key": state["current_section_key"]
    }

def compile_tutorial(state: GraphState) -> GraphState:
    """Compiles all written sections into a final tutorial document."""
    print("---AGENT: Compiling Final Tutorial---")
    outline = state['tutorial_outline']
    drafts = state['section_drafts']
    final_md = f"# {outline['title']}\n\n"
    for i, section in enumerate(outline['sections']):
        final_md += f"## {i+1}. {section['title']}\n\n"
        final_md += drafts.get(str(i), "Error: Content for this section was not generated.") + "\n\n"
    return {
        "original_query": state["original_query"],
        "scraped_content": state["scraped_content"],
        "tutorial_outline": state["tutorial_outline"],
        "section_drafts": state["section_drafts"],
        "final_tutorial": final_md,
        "error_message": state["error_message"],
        "current_section_key": state["current_section_key"]
    }

# --- CONDITIONAL LOGIC ---

def should_continue(state: GraphState) -> str:
    """Determines whether to write another section or compile the tutorial."""
    if state.get("error_message"):
        return "end"
        
    drafts = state['section_drafts']
    outline_sections = state['tutorial_outline']['sections']
    
    if len(drafts) < len(outline_sections):
        next_section_key = str(len(drafts))
        state['current_section_key'] = next_section_key
        return "write_section"
    else:
        return "compile_tutorial"

# --- BUILD THE GRAPH ---

def create_tutorial_graph():
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("generate_outline", generate_outline)
    workflow.add_node("write_section", write_section)
    workflow.add_node("compile_tutorial", compile_tutorial)
    workflow.add_node("should_continue", should_continue)

    # Set entry point
    workflow.set_entry_point("generate_outline")

    # Add edges
    workflow.add_edge("write_section", "should_continue")
    workflow.add_edge("compile_tutorial", END)

    # Add conditional edge
    workflow.add_conditional_edges(
        "generate_outline",
        lambda state: "compile_tutorial" if state.get("error_message") else "should_continue",
        {
            "should_continue": "should_continue",
            "compile_tutorial": "compile_tutorial"
        }
    )
    workflow.add_conditional_edges(
        "should_continue",
        should_continue,
        {
            "write_section": "write_section",
            "compile_tutorial": "compile_tutorial"
        }
    )

    # Compile the graph
    app = workflow.compile()
    return app