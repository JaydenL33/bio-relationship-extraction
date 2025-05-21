import streamlit as st
from helper.api import post_data_to_api
from helper.helpers import check_duplicate_relationship

def validate_relationships_page(neo4j_connector):
    st.header("Validate Extracted Relationships")
    
    # Check if we have relationships to validate
    if len(st.session_state.relationships) == 0:
        st.info("No relationships to validate. Please search for papers and extract relationships first.")
        return
    
    # Display progress
    total_rels = len(st.session_state.relationships)
    current_index = st.session_state.current_rel_index
    st.progress(current_index / total_rels)
    st.write(f"Reviewing relationship {current_index + 1} of {total_rels}")
    
    if current_index >= total_rels:
        st.success("All relationships have been validated!")
        if st.button("Start Over"):
            st.session_state.current_rel_index = 0
            st.rerun()
        return
    
    current_rel = st.session_state.relationships[current_index]
    
    # Validate current relationship has all required fields
    required_fields = ['subject', 'subject_type', 'predicate', 'object', 'object_type']
    is_valid = all(field in current_rel for field in required_fields)
    
    if not is_valid:
        st.error("The current relationship is missing required fields.")
        st.write("Relationship data:", current_rel)
        if st.button("Skip Invalid Relationship"):
            st.session_state.current_rel_index += 1
            st.rerun()
        return
    
    # Check for duplicates in Neo4j
    is_duplicate = check_duplicate_relationship(neo4j_connector, current_rel)
    
    # Display the relationship card in a nice box
    st.subheader("Relationship Card")
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 3])
        
        with col1:
            st.markdown(f"**Subject**: {current_rel['subject']}")
            st.markdown(f"**Type**: {current_rel['subject_type']}")
        
        with col2:
            st.markdown(f"**→ {current_rel['predicate']} →**")
        
        with col3:
            st.markdown(f"**Object**: {current_rel['object']}")
            st.markdown(f"**Type**: {current_rel['object_type']}")
        
        st.markdown("---")
        # Use get() to safely access optional fields
        paper_title = current_rel.get('paper_title', 'Unknown Paper')
        context = current_rel.get('context', 'No context provided')
        
        st.markdown(f"**Source Paper**: {paper_title}")
        st.markdown(f"**Excerpt**: \"{context}\"")
    
    # Warning for duplicates
    if is_duplicate:
        st.warning("⚠️ This relationship may already exist in the knowledge graph.")
    
    # Buttons for validation
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("👍 Confirm", key="confirm_btn"):
            # Call API to store the confirmed relationship
            try:
                # Convert to API format
                relationship_data = {
                    "entity1": current_rel['subject'],
                    "relation": current_rel['predicate'],
                    "entity2": current_rel['object']
                }
                
                # Send to Neo4j add relationship endpoint
                response = post_data_to_api("neo4j/add_relationship/", relationship_data)
                
                if response and response[0].get("message") == "Relationship added successfully":
                    st.success("Relationship confirmed and added to the knowledge graph!")
                else:
                    st.error(f"Error: {response[0].get('error', 'Unknown error')}")
            except Exception as e:
                st.error(f"Error connecting to API: {str(e)}")
            
            # Move to next relationship
            st.session_state.current_rel_index += 1
            st.rerun()
    
    with col2:
        if st.button("👎 Reject", key="reject_btn"):
            # Skip this relationship
            st.session_state.current_rel_index += 1
            st.rerun()