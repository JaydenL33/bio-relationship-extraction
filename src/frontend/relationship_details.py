import streamlit as st
import time
from helper.neo4j_connector import Neo4jConnector

def show_relationship_details(neo4j_connector: Neo4jConnector):
    st.header("Relationship Confirmation")
    
    # Check if we have a confirmed relationship to display
    if "last_confirmed_relationship" not in st.session_state:
        st.info("No relationship has been confirmed yet.")
        if st.button("Return to Validation"):
            st.session_state.show_relationship_details = False
        return
    
    rel = st.session_state.last_confirmed_relationship
    
    # Display success message
    st.success("Relationship successfully added to the knowledge graph!")
    
    # Show the confirmed relationship details
    st.subheader("Confirmed Relationship")
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 3])
        with col1:
            st.markdown(f"**Subject**: {rel['subject']}")
            st.markdown(f"**Type**: {rel['subject_type']}")
        with col2:
            st.markdown(f"**→ {rel['predicate']} →**")
        with col3:
            st.markdown(f"**Object**: {rel['object']}")
            st.markdown(f"**Type**: {rel['object_type']}")
        
        st.markdown("---")
        paper_title = rel.get('paper_title', 'Unknown Paper')
        context = rel.get('context', 'No context provided')
        st.markdown(f"**Source Paper**: {paper_title}")
        st.markdown(f"**Excerpt**: \"{context}\"")
    
    # Display progress
    if "relationships" in st.session_state:
        total_rels = len(st.session_state.relationships)
        current_index = st.session_state.current_rel_index
        remaining = total_rels - current_index
        
        st.write(f"You have reviewed {current_index} out of {total_rels} relationships")
        st.write(f"{remaining} relationships remaining")
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Continue to Next Relationship"):
            st.session_state.show_relationship_details = False
            # Reset notification if present
            if "result_notification" in st.session_state:
                st.session_state.result_notification = None
    
    with col2:
        if st.button("Return to Main Menu"):
            st.session_state.show_relationship_details = False
            # Set flag to return to Paper Management page
            st.session_state.return_to_main = True
