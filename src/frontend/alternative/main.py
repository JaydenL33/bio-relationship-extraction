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
    st.set_page_config(page_title="PubMed Knowledge Graph Builder", layout="wide")
    st.title("PubMed Knowledge Graph Builder")
    
    # Initialize session state
    if "current_rel_index" not in st.session_state:
        st.session_state.current_rel_index = 0
    if "relationships" not in st.session_state:
        st.session_state.relationships = []
    
    # Connect to the Neo4J database
    neo4j_connector = Neo4jConnector(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    neo4j_connector.connect()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Search Papers", "Validate Relationships", "View Knowledge Graph"])
    
    if page == "Search Papers":
        search_papers_page()
    elif page == "Validate Relationships":
        validate_relationships_page(neo4j_connector)
    elif page == "View Knowledge Graph":
        view_graph_page(neo4j_connector)
    
    # Close the Neo4J connection when app closes
    neo4j_connector.close()

# Run the app
if __name__ == "__main__":
    main()