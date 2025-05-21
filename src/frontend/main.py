import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import matplotlib.pyplot as plt


# Import local modules
from helper.api import get_data_from_api, post_data_to_api
from helper.neo4j_connector import Neo4jConnector
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from paper_search import search_papers_page
from confirm_relationships import validate_relationships_page  
from knowledger_graph import view_graph_page

def main():
    st.set_page_config(page_title="Biomedical Knowledge Graph Builder", layout="wide")
    st.title("Biomedical Knowledge Graph Builder")
    
    # Initialize session state
    if "current_rel_index" not in st.session_state:
        st.session_state.current_rel_index = 0
    if "relationships" not in st.session_state:
        st.session_state.relationships = []
    if "redirect_to_validate" not in st.session_state:
        st.session_state.redirect_to_validate = False
    if "result_notification" not in st.session_state:
        st.session_state.result_notification = None
    
    # Connect to the Neo4J database
    neo4j_connector = Neo4jConnector(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    connected = neo4j_connector.connect()
    if not connected:
        st.sidebar.error("⚠️ Cannot connect to Neo4j database. Please check your connection settings.")
    
    # Check if we can connect to the API
    health_check = get_data_from_api("health")
    if not health_check:
        st.sidebar.error("⚠️ Cannot connect to the backend API. Please ensure it's running.")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    
    # Handle redirection from paper search to validation
    if st.session_state.redirect_to_validate:
        st.session_state.redirect_to_validate = False
        page = "Validate Relationships"
    else:
        page = st.sidebar.radio("Go to", ["Paper Management", "Validate Relationships", "View Knowledge Graph"])
    
    # Display page based on selection
    if page == "Paper Management":
        search_papers_page()
    elif page == "Validate Relationships":
        validate_relationships_page(neo4j_connector)
    elif page == "View Knowledge Graph":
        view_graph_page(neo4j_connector)
    
    # Debug information in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("Debug Info")
    st.sidebar.write(f"Current page: {page}")
    st.sidebar.write(f"Relationships to validate: {len(st.session_state.get('relationships', []))}")
    st.sidebar.write(f"Current index: {st.session_state.get('current_rel_index', 0)}")
    
    # Close the Neo4J connection when app closes
    try:
        neo4j_connector.close()
    except:
        pass

# Run the app
from streamlit.web import cli as stcli
from streamlit import runtime
import sys

if __name__ == '__main__':
    if runtime.exists():
        main()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())