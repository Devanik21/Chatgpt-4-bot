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

def parse_markdown_to_graphviz(markdown_text: str, topic: str, orientation: str = "LR", font_size: int = 12, node_color: str = "#ADD8E6", max_depth: int = 5) -> graphviz.Digraph:
    """
    Parses a markdown nested list into a graphviz Digraph object.
    Supports orientation, font size, node color, and depth limit.
    """
    dot = graphviz.Digraph('MindMap', comment=f'Mind Map for {topic}')
    dot.attr('node', shape='box', style='rounded,filled', fillcolor=node_color, fontname='Helvetica', fontsize=str(font_size))
    dot.attr('edge', color='gray', fontname='Helvetica')
    orientation_map = {
        "Left-Right (LR)": "LR",
        "Top-Bottom (TB)": "TB",
        "Right-Left (RL)": "RL",
        "Bottom-Top (BT)": "BT"
    }
    dot.attr(rankdir=orientation_map.get(orientation, "LR"), splines='ortho')

    lines = markdown_text.strip().split('\n')
    parent_stack = []
    existing_ids = set()

    for line in lines:
        if not line.strip():
            continue

        stripped_line = line.lstrip()
        indentation = len(line) - len(stripped_line)
        level = indentation // 2

        if level >= max_depth:
            continue

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
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = MIND_MAP_PROMPT.format(topic=topic)
    response = model.generate_content(prompt)
    return response.text

# --- Streamlit UI ---

st.title("🧠 Mind-Map Generator")
st.markdown("Give Gemini a topic, and it will produce a hierarchical mind map outline, which is then rendered visually. Perfect for brainstorming!")

# --- Sidebar for API Key and Advanced Options ---
st.sidebar.title("Configuration")
st.sidebar.markdown("Enter your Google API Key to get started.")
api_key = st.sidebar.text_input(
    "Google API Key", type="password", help="Get your key from [Google AI Studio](https://aistudio.google.com/app/apikey)."
)

# --- Advanced Features ---
st.sidebar.markdown("---")
st.sidebar.header("Advanced Options")

theme = st.sidebar.selectbox("Theme", ["Light", "Dark", "Custom"])
max_depth = st.sidebar.slider("Mind Map Depth Limit", min_value=1, max_value=10, value=5)
show_markdown = st.sidebar.checkbox("Show Raw Markdown", value=True)
show_export = st.sidebar.checkbox("Show Export Options", value=True)
orientation = st.sidebar.selectbox("Orientation", ["Left-Right (LR)", "Top-Bottom (TB)", "Right-Left (RL)", "Bottom-Top (BT)"], index=0)
font_size = st.sidebar.slider("Node Font Size", min_value=8, max_value=32, value=12)
node_color = st.sidebar.color_picker("Node Color", "#ADD8E6")
regenerate = st.sidebar.button("🔄 Regenerate Mind Map")

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

if st.button("✨ Generate Mind Map", disabled=not topic_seed) or regenerate:
    with st.spinner(f"Generating mind map for '{topic_seed}'..."):
        try:
            markdown_output = generate_mind_map(topic_seed)
            graph = parse_markdown_to_graphviz(
                markdown_output, topic_seed,
                orientation=orientation,
                font_size=font_size,
                node_color=node_color,
                max_depth=max_depth
            )
            st.graphviz_chart(graph)

            # Show/hide raw markdown
            if show_markdown:
                st.subheader("Raw Outline (Markdown)")
                st.code(markdown_output, language="markdown")
                st.button("Copy Markdown to Clipboard", on_click=lambda: st.session_state.update({"_clipboard": markdown_output}), key="copy_md")

            # Show/hide export options
            if show_export:
                st.subheader("Export Options")
                col1, col2, col3 = st.columns(3)
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
                    st.button("Copy DOT to Clipboard", on_click=lambda: st.session_state.update({"_clipboard": graph.source}), key="copy_dot")
                with col3:
                    try:
                        import tempfile
                        import os
                        png_bytes = None
                        with tempfile.TemporaryDirectory() as tmpdir:
                            png_path = os.path.join(tmpdir, "mindmap.png")
                            graph.render(filename=png_path, format="png", cleanup=True)
                            with open(png_path + ".png", "rb") as f:
                                png_bytes = f.read()
                        if png_bytes:
                            st.download_button(
                                label="Download as PNG",
                                data=png_bytes,
                                file_name=f"{topic_seed}_mindmap.png",
                                mime="image/png"
                            )
                    except Exception:
                        st.info("Graphviz PNG export requires Graphviz installed on the server.")

        except Exception as e:
            st.error(f"An error occurred while generating the mind map: {e}")
            st.info("This could be due to an invalid API key or a content safety issue from the model.")
