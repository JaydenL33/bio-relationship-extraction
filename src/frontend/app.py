import streamlit as st
import requests
from streamlit_agraph import agraph, Node, Edge, Config

# Placeholder API functions (to be replaced with actual endpoints)
def extract_relationships(query):
    """Query the API to extract relationships based on user query."""
    # Placeholder: Replace with actual API call
    # response = requests.post("http://api-url/extract_relationships", json={"query": query})
    # return response.json()["relationships"]
    return [
        {"id": 1, "entity1": "Metabolite_A", "relationship_type": "ISOLATED_FROM", "entity2": "Species_X"},
        {"id": 2, "entity1": "Metabolite_B", "relationship_type": "ISOLATED_FROM", "entity2": "Species_Y"}
    ]

def save_relationships(relationships):
    """Send confirmed relationships to the API for saving in Neo4j."""
    # Placeholder: Replace with actual API call
    # response = requests.post("http://api-url/save_relationships", json={"relationships": relationships})
    # return response.status_code == 200
    return True

def get_graph():
    """Retrieve the current knowledge graph from the API."""
    # Placeholder: Replace with actual API call
    # response = requests.get("http://api-url/get_graph")
    # return response.json()
    return {
        "nodes": [Node(id=1, label="Metabolite_A"), Node(id=2, label="Species_X")],
        "edges": [Edge(source=1, target=2, label="ISOLATED_FROM")]
    }

# Initialize session state
if "proposed_relationships" not in st.session_state:
    st.session_state.proposed_relationships = []
if "choices" not in st.session_state:
    st.session_state.choices = {}

# UI Layout
st.title("Knowledge Graph Builder")

# Sidebar: Input Controls
with st.sidebar:
    st.header("Search and Query")
    # Keyword input for paper search
    keywords = st.text_input("Enter keywords to search papers:", placeholder="e.g., cancer biomarkers")
    query = st.text_input("Enter query for relationship extraction:", placeholder="e.g., metabolites in species")
    
    if st.button("Extract Relationships"):
        if query:
            with st.spinner("Extracting relationships..."):
                st.session_state.proposed_relationships = extract_relationships(query)
                st.session_state.choices = {f"choice_{rel['id']}": "No" for rel in st.session_state.proposed_relationships}
            st.success(f"Found {len(st.session_state.proposed_relationships)} proposed relationships.")
        else:
            st.warning("Please enter a query.")

# Main Area: Relationship Validation and Graph Visualization
col1, col2 = st.columns([2, 3])

with col1:
    st.header("Relationship Validation")
    if st.session_state.proposed_relationships:
        with st.form("validation_form"):
            for rel in st.session_state.proposed_relationships:
                st.write(f"{rel['entity1']} {rel['relationship_type']} {rel['entity2']}")
                st.session_state.choices[f"choice_{rel['id']}"] = st.radio(
                    "Confirm this relationship?", ["Yes", "No"], index=1, key=f"choice_{rel['id']}"
                )
            submitted = st.form_submit_button("Submit Validations")
        
        if submitted:
            confirmed = [
                rel for rel in st.session_state.proposed_relationships
                if st.session_state.choices[f"choice_{rel['id']}"] == "Yes"
            ]
            if save_relationships(confirmed):
                st.success(f"Saved {len(confirmed)} relationships to Neo4j.")
                st.session_state.proposed_relationships = []
                st.session_state.choices = {}
            else:
                st.error("Failed to save relationships.")
    else:
        st.info("No relationships to validate. Enter a query to begin.")

with col2:
    st.header("Knowledge Graph")
    if st.button("View Graph"):
        with st.spinner("Loading graph..."):
            graph_data = get_graph()
            nodes = graph_data["nodes"]
            edges = graph_data["edges"]
            config = Config(width=500, height=400, directed=True, nodeHighlightBehavior=True)
            agraph(nodes=nodes, edges=edges, config=config)