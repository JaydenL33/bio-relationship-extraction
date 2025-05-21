import streamlit as st
import pandas as pd
from pyvis.network import Network

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

def build_graph_query(entity_type, relationship_type, keyword_filter="", max_nodes=50):
    """Build a Cypher query based on filters"""
    where_clauses = []
    
    if keyword_filter:
        where_clauses.append(f"(n.name CONTAINS '{keyword_filter}' OR m.name CONTAINS '{keyword_filter}')")
    
    where_clause = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    
    if entity_type == "All" and relationship_type == "All":
        return f"MATCH (n)-[r]->(m){where_clause} RETURN n, r, m LIMIT {max_nodes}"
    elif entity_type == "All":
        return f"MATCH (n)-[r:{relationship_type}]->(m){where_clause} RETURN n, r, m LIMIT {max_nodes}"
    elif relationship_type == "All":
        return f"MATCH (n:{entity_type})-[r]->(m){where_clause} RETURN n, r, m LIMIT {max_nodes}"
    else:
        return f"MATCH (n:{entity_type})-[r:{relationship_type}]->(m){where_clause} RETURN n, r, m LIMIT {max_nodes}"

def create_interactive_graph(graph_data):
    """Create an interactive network visualization using pyvis"""
    net = Network(height="550px", width="100%", bgcolor="#FFFFFF", font_color="black")
    
    # Add nodes and edges
    added_nodes = set()
    
    for record in graph_data:
        source_id = str(record['n'].id)
        source_name = record['n'].get('name', source_id)
        source_type = list(record['n'].labels)[0] if record['n'].labels else ""
        
        target_id = str(record['m'].id)
        target_name = record['m'].get('name', target_id)
        target_type = list(record['m'].labels)[0] if record['m'].labels else ""
        
        relationship = record['r'].type
        
        # Add nodes
        if source_id not in added_nodes:
            net.add_node(source_id, label=source_name, title=f"{source_name} ({source_type})", 
                         color=get_node_color(source_type), group=source_type)
            added_nodes.add(source_id)
            
        if target_id not in added_nodes:
            net.add_node(target_id, label=target_name, title=f"{target_name} ({target_type})", 
                         color=get_node_color(target_type), group=target_type)
            added_nodes.add(target_id)
        
        # Add edge
        net.add_edge(source_id, target_id, label=relationship, title=relationship)
    
    # Set physics options for better visualization
    net.set_options("""
    {
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -50,
          "centralGravity": 0.01,
          "springLength": 200,
          "springConstant": 0.08
        },
        "solver": "forceAtlas2Based",
        "stabilization": {
          "iterations": 100
        }
      },
      "interaction": {
        "navigationButtons": true,
        "keyboard": true
      }
    }
    """)
    
    # Save and return the HTML
    html_path = "temp_network.html"
    net.save_graph(html_path)
    
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    return html_content

def get_node_color(node_type):
    """Return a color based on node type"""
    color_map = {
        "Gene": "#4285F4",     # Blue
        "Protein": "#34A853",  # Green
        "Drug": "#FBBC05",     # Yellow
        "Disease": "#EA4335",  # Red
        "Species": "#9C27B0",  # Purple
        "Metabolite": "#FF9800", # Orange
        "Pathway": "#2196F3"   # Light Blue
    }
    return color_map.get(node_type, "#607D8B")  # Default gray

def display_graph_as_table(graph_data):
    """Display graph data in a tabular format"""
    rows = []
    for record in graph_data:
        source = record['n'].get('name', str(record['n'].id))
        source_type = list(record['n'].labels)[0] if record['n'].labels else ""
        target = record['m'].get('name', str(record['m'].id))
        target_type = list(record['m'].labels)[0] if record['m'].labels else ""
        relationship = record['r'].type
        
        rows.append({
            "Subject": source,
            "Subject Type": source_type,
            "Relationship": relationship,
            "Object": target,
            "Object Type": target_type
        })
    
    if rows:
        st.dataframe(pd.DataFrame(rows))

def convert_graph_to_csv(graph_data):
    """Convert graph data to CSV format for download"""
    rows = []
    for record in graph_data:
        source = record['n'].get('name', str(record['n'].id))
        source_type = list(record['n'].labels)[0] if record['n'].labels else ""
        target = record['m'].get('name', str(record['m'].id))
        target_type = list(record['m'].labels)[0] if record['m'].labels else ""
        relationship = record['r'].type
        
        rows.append(f"{source},{source_type},{relationship},{target},{target_type}")
    
    header = "Subject,SubjectType,Relationship,Object,ObjectType\n"
    return header + "\n".join(rows)
