import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import matplotlib.pyplot as plt
import json
import html

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
    
    # Connect to the Neo4J database
    neo4j_connector = Neo4jConnector(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    try:
        neo4j_connector.connect()
        # Check if we can connect to the API
        health_check = get_data_from_api("health")
        if not health_check:
            st.sidebar.error("⚠️ Cannot connect to the backend API. Please ensure it's running.")
    except Exception as e:
        st.sidebar.error(f"⚠️ Error connecting to Neo4j: {str(e)}")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Paper Management", "Validate Relationships", "View Knowledge Graph"])
    
    if page == "Paper Management":
        search_papers_page()
    elif page == "Validate Relationships":
        validate_relationships_page(neo4j_connector)
    elif page == "View Knowledge Graph":
        view_graph_page(neo4j_connector)
    
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