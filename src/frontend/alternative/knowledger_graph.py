import streamlit as st
import pandas as pd
from helper.helpers import build_graph_query, create_interactive_graph, display_graph_as_table, convert_graph_to_csv

def view_graph_page(neo4j_connector):
    st.header("Knowledge Graph Visualization")
    
    # Options for filtering the graph
    st.subheader("Filter Options")
    col1, col2 = st.columns(2)
    
    with col1:
        entity_type = st.selectbox("Filter by Entity Type:", 
                                  ["All", "Gene", "Protein", "Drug", "Disease", 
                                   "Species", "Metabolite", "Pathway"])
    
    with col2:
        relationship_type = st.selectbox("Filter by Relationship Type:", 
                                        ["All", "INHIBITS", "ACTIVATES", "TREATS", 
                                         "CAUSES", "INTERACTS_WITH", "ISOLATED_FROM", 
                                         "ASSOCIATED_WITH", "PART_OF"])
    
    # Additional filter options
    with st.expander("Advanced Filters"):
        keyword_filter = st.text_input("Filter by keyword in entity name:")
        max_nodes = st.slider("Maximum number of nodes to display", 10, 200, 50)
    
    # Query to get graph data based on filters
    query = build_graph_query(entity_type, relationship_type, keyword_filter, max_nodes)
    
    # Fetch and visualize graph
    if st.button("Visualize Graph"):
        with st.spinner("Generating visualization..."):
            try:
                graph_data = neo4j_connector.fetch_data(query)
                
                if not graph_data or len(graph_data) == 0:
                    st.warning("No data found for the selected filters.")
                else:
                    # Create interactive network visualization
                    st.subheader(f"Knowledge Graph ({len(graph_data)} relationships)")
                    html_content = create_interactive_graph(graph_data)
                    st.components.v1.html(html_content, height=600)
                    
                    # Display results in table format
                    st.subheader("Tabular View")
                    display_graph_as_table(graph_data)
                    
                    # Option to download graph data
                    csv_data = convert_graph_to_csv(graph_data)
                    st.download_button(
                        label="Download Graph Data (CSV)",
                        data=csv_data,
                        file_name="knowledge_graph.csv",
                        mime="text/csv"
                    )
            except Exception as e:
                st.error(f"Error retrieving or visualizing graph data: {str(e)}")