import streamlit as st
import pandas as pd
from pyvis.network import Network
import html
import tempfile
import os
import io

def check_duplicate_relationship(neo4j_connector, relationship):
    """Check if a relationship already exists in Neo4j"""
    # Validate that the relationship dictionary has all required keys
    required_keys = ['subject_type', 'predicate', 'object_type', 'subject', 'object']
    missing_keys = [key for key in required_keys if key not in relationship]
    
    if missing_keys:
        st.warning(f"Relationship is missing required keys: {', '.join(missing_keys)}")
        st.write("Relationship data:", relationship)
        return False  # Can't check for duplicates with missing data
    
    # Safe extraction of values with fallbacks for any missing keys
    subject_type = relationship.get('subject_type', 'Entity')
    predicate = relationship.get('predicate', 'RELATED_TO')
    object_type = relationship.get('object_type', 'Entity')
    
    # Build the query with proper escaping for Neo4j label names
    # We use explicit string formatting rather than relying on Neo4j parameter substitution for label names
    query = """
    MATCH (s:{subject_type} {{name: $subject_name}})-
          [r:{predicate}]->
          (o:{object_type} {{name: $object_name}})
    RETURN count(r) as count
    """.format(
        subject_type=subject_type,
        predicate=predicate,
        object_type=object_type
    )
    
    params = {
        "subject_name": relationship.get('subject', ''),
        "object_name": relationship.get('object', '')
    }
    
    try:
        result = neo4j_connector.fetch_data(query, params)
        return result[0]['count'] > 0 if result else False
    except Exception as e:
        st.error(f"Error checking for duplicate relationship: {e}")
        return False  # Assume no duplicate if there's an error

def build_graph_query(relationship_type, keyword_filter, max_nodes):
    """
    Build a Cypher query based on filter options.
    
    Args:
        entity_type: Type of entity to filter by
        relationship_type: Type of relationship to filter by
        keyword_filter: Keyword to filter entity names
        max_nodes: Maximum number of nodes to return
        
    Returns:
        str: A Cypher query for Neo4j
    """
    # Base query
    query = "MATCH (n1)-[r]->(n2)"
    
    # Add filters
    filters = []
    
    if relationship_type != "ALL":
        filters.append(f"type(r) = '{relationship_type}'")
    
    if keyword_filter:
        filters.append(f"(n1.name CONTAINS '{keyword_filter}' OR n2.name CONTAINS '{keyword_filter}')")
    
    # Combine filters if any
    if filters:
        query += " WHERE " + " AND ".join(filters)
    
    # Add limit and return
    query += f" RETURN n1, r, n2 LIMIT {max_nodes}"
    
    return query

def create_interactive_graph(graph_data):
    """
    Create an interactive graph visualization using PyVis.
    
    Args:
        graph_data: List of graph data from Neo4j
        
    Returns:
        str: HTML content of the graph
    """
    # Initialize a new network
    print(graph_data)
    net = Network(height="550px", width="100%", bgcolor="#FFFFFF", 
                 directed=True, notebook=False, cdn_resources="remote")
    
    # Set physics options for better layout
    net.barnes_hut(gravity=-50, central_gravity=0.01, spring_length=200, spring_strength=0.08)
    net.toggle_physics(True)
    
    # Track added nodes to avoid duplicates
    added_nodes = set()
    
    # Process graph data
    for item in graph_data:
        # Extract source and target nodes
        source = item.get('n1', {})
        target = item.get('n2', {})
        rel = item.get('r', {})
        
        # Extract node properties
        source_id = source.get('id', str(hash(source.get('name', ''))))
        source_label = source.get('name', 'Unknown')
        source_type = source.get('type', 'Entity')
        
        target_id = target.get('id', str(hash(target.get('name', ''))))
        target_label = target.get('name', 'Unknown')
        target_type = target.get('type', 'Entity')
        
        # Add source node if not already added
        if source_id not in added_nodes:
            net.add_node(source_id, label=source_label, title=f"{source_label} ({source_type})",
                        group=source_type, shape="dot")
            added_nodes.add(source_id)
        
        # Add target node if not already added
        if target_id not in added_nodes:
            net.add_node(target_id, label=target_label, title=f"{target_label} ({target_type})",
                        group=target_type, shape="dot")
            added_nodes.add(target_id)
        
        # Add edge - handling tuple structure of relationship
        if isinstance(rel, tuple) and len(rel) >= 2:
            # The relationship type is the middle element of the tuple
            rel_type = rel[1]
        else:
            # Fallback for dictionary format or other formats
            rel_type = rel.get('type', 'RELATED_TO') if isinstance(rel, dict) else 'RELATED_TO'
            
        net.add_edge(source_id, target_id, label=rel_type, title=rel_type)
    
    # Generate and return the html content
    with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp:
        path = tmp.name
        net.save_graph(path)
        with open(path, 'r', encoding='utf-8') as file:
            html_string = file.read()
        os.unlink(path)  # Remove the temporary file
    
    return html_string

def display_graph_as_table(graph_data):
    """
    Display graph data as a table in Streamlit.
    
    Args:
        graph_data: List of graph data from Neo4j
    """
    rows = []
    for item in graph_data:
        source = item.get('n1', {})
        target = item.get('n2', {})
        rel = item.get('r', {})
        
        # Determine relationship type based on data structure
        if isinstance(rel, tuple) and len(rel) >= 2:
            # The relationship type is the middle element of the tuple
            relationship_type = rel[1]
        else:
            # Fallback for dictionary format or other formats
            relationship_type = rel.get('type', 'RELATED_TO') if isinstance(rel, dict) else 'RELATED_TO'
        
        rows.append({
            'Source': source.get('name', 'Unknown'),
            'Source Type': source.get('type', 'Entity'),
            'Relationship': relationship_type,
            'Target': target.get('name', 'Unknown'),
            'Target Type': target.get('type', 'Entity')
        })
    
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df)
    else:
        st.info("No relationships to display")

def convert_graph_to_csv(graph_data):
    """
    Convert graph data to CSV format for download.
    
    Args:
        graph_data: List of graph data from Neo4j
        
    Returns:
        str: CSV data
    """
    rows = []
    for item in graph_data:
        source = item.get('n1', {})
        target = item.get('n2', {})
        rel = item.get('r', {})
        
        # Determine relationship type based on data structure
        if isinstance(rel, tuple) and len(rel) >= 2:
            # The relationship type is the middle element of the tuple
            relationship_type = rel[1]
        else:
            # Fallback for dictionary format or other formats
            relationship_type = rel.get('type', 'RELATED_TO') if isinstance(rel, dict) else 'RELATED_TO'
        
        rows.append({
            'Source': source.get('name', 'Unknown'),
            'Source Type': source.get('type', 'Entity'),
            'Relationship': relationship_type,
            'Target': target.get('name', 'Unknown'),
            'Target Type': target.get('type', 'Entity')
        })
    
    if not rows:
        return "No data"
    
    df = pd.DataFrame(rows)
    csv_data = df.to_csv(index=False)
    return csv_data
