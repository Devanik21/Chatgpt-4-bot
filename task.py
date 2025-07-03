import streamlit as st
import google.generativeai as genai
import graphviz
import re

# --- Configuration ---
st.set_page_config(
    page_title="Mind-Map Generator",
    page_icon="🧠",
    layout="wide"
)

# --- Gemini API Configuration ---
# The API key is now configured via the sidebar input.
# --- Prompt Template ---
MIND_MAP_PROMPT = """
You are an expert mind map creator.
Your task is to generate a hierarchical mind map outline for the given topic.
The output must be a markdown-formatted nested list.
Each item in the list represents a node in the mind map.
Use indentation (two spaces per level) to represent the hierarchy.
Do not include any other text, explanations, or markdown formatting like headers or backticks.
The root of the mind map should be the topic itself.

**Example for "Data Structures":**
- Data Structures
  - Linear
    - Array
    - Linked List
    - Stack
    - Queue
  - Non-Linear
    - Tree
      - Binary Tree
      - B-Tree
    - Graph

**Generate a mind map for the topic:** "{topic}"
"""

# --- Helper Functions ---

def generate_unique_node_id(text, existing_ids):
    """Generates a unique, safe ID for a graphviz node."""
    base_id = re.sub(r'\W+', '_', text).lower()
    node_id = base_id
    counter = 1
    while node_id in existing_ids:
        node_id = f"{base_id}_{counter}"
        counter += 1
    return node_id

def parse_markdown_to_graphviz(markdown_text: str, topic: str) -> graphviz.Digraph:
    """
    Parses a markdown nested list into a graphviz Digraph object.
    """
    dot = graphviz.Digraph('MindMap', comment=f'Mind Map for {topic}')
    dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue', fontname='Helvetica')
    dot.attr('edge', color='gray', fontname='Helvetica')
    dot.attr(rankdir='LR', splines='ortho') # Left-to-Right layout

    lines = markdown_text.strip().split('\n')
    parent_stack = [] # A stack of (level, node_id)
    existing_ids = set()

    for line in lines:
        if not line.strip():
            continue

        stripped_line = line.lstrip()
        indentation = len(line) - len(stripped_line)
        level = indentation // 2  # Assuming 2 spaces per indent level

        node_text = stripped_line.lstrip('- ').strip()
        node_id = generate_unique_node_id(node_text, existing_ids)
        existing_ids.add(node_id)

        dot.node(node_id, node_text)

        while parent_stack and parent_stack[-1][0] >= level:
            parent_stack.pop()

        if parent_stack:
            parent_id = parent_stack[-1][1]
            dot.edge(parent_id, node_id)

        parent_stack.append((level, node_id))

    return dot

def generate_mind_map(topic: str):
    """Calls the Gemini API to generate the mind map markdown."""
    model = genai.GenerativeModel('gemini-pro')
    prompt = MIND_MAP_PROMPT.format(topic=topic)
    response = model.generate_content(prompt)
    return response.text

# --- Streamlit UI ---

st.title("🧠 Mind-Map Generator")
st.markdown("Give Gemini a topic, and it will produce a hierarchical mind map outline, which is then rendered visually. Perfect for brainstorming!")

# --- Sidebar for API Key ---
st.sidebar.title("Configuration")
st.sidebar.markdown("Enter your Google API Key to get started.")
api_key = st.sidebar.text_input(
    "Google API Key", type="password", help="Get your key from [Google AI Studio](https://aistudio.google.com/app/apikey)."
)

# --- Main App Logic ---
if not api_key:
    st.info("Please enter your Google API Key in the sidebar to use the generator.")
    st.stop()

# Configure the API key once it's provided
try:
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"Error configuring the Google API: {e}")
    st.stop()


topic_seed = st.text_input("Enter a topic seed:", "The Link Data Structure")

if st.button("✨ Generate Mind Map", disabled=not topic_seed):
    with st.spinner(f"Generating mind map for '{topic_seed}'..."):
        try:
            markdown_output = generate_mind_map(topic_seed)
            graph = parse_markdown_to_graphviz(markdown_output, topic_seed)
            st.graphviz_chart(graph)
            st.subheader("Raw Outline (Markdown)")
            st.code(markdown_output, language="markdown")

            # --- Export Options ---
            st.subheader("Export Options")
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="Download Markdown",
                    data=markdown_output,
                    file_name=f"{topic_seed}_mindmap.md",
                    mime="text/markdown"
                )
            with col2:
                st.download_button(
                    label="Download Graphviz DOT",
                    data=graph.source,
                    file_name=f"{topic_seed}_mindmap.dot",
                    mime="text/vnd.graphviz"
                )
        except Exception as e:
            st.error(f"An error occurred while generating the mind map: {e}")
            st.info("This could be due to an invalid API key or a content safety issue from the model.")
