import streamlit as st
import pandas as pd
from helper.helpers import build_graph_query, create_interactive_graph, display_graph_as_table, convert_graph_to_csv

def view_graph_page(neo4j_connector):
    st.header("Knowledge Graph Visualisation")
    
    # Options for filtering the graph
    st.subheader("Filter Options")
    cols = st.columns(1)
    
    with cols[0]:
        relationship_type = st.selectbox("Filter by Relationship Type:", 
                                        ["ALL", "ISOLATED_FROM", "METABOLITE_OF", "PRODUCES", "DEGRADED_BY", 
                                         "BIOSYNTHESIZED_BY", "INHIBITS", "PRECURSOR_OF", 
                                         "UPTAKEN_BY", "MODIFIES", "SEQUESTERS", "CONTAINS"])
    
    # Additional filter options
    with st.expander("Advanced Filters"):
        keyword_filter = st.text_input("Filter by keyword in entity name:")
        max_nodes = st.slider("Maximum number of nodes to display", 10, 200, 50)
    
    # Query to get graph data based on filters
    query = build_graph_query(relationship_type, keyword_filter, max_nodes)
    
    # Fetch and visualize graph
    if st.button("Visualise Graph"):
        with st.spinner("Generating visualisation..."):
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