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
            st.experimental_rerun()
        return
    
    current_rel = st.session_state.relationships[current_index]
    
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
        st.markdown(f"**Source Paper**: {current_rel['paper_title']}")
        st.markdown(f"**Excerpt**: \"{current_rel['context']}\"")
    
    # Warning for duplicates
    if is_duplicate:
        st.warning("⚠️ This relationship may already exist in the knowledge graph.")
    
    # Buttons for validation
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("👍 Confirm", key="confirm_btn"):
            # Call API to store the confirmed relationship
            try:
                response = post_data_to_api("relationships/confirm", current_rel)
                if response.get("success"):
                    st.success("Relationship confirmed and added to the knowledge graph!")
                else:
                    st.error(f"Error: {response.get('error', 'Unknown error')}")
            except Exception as e:
                st.error(f"Error connecting to API: {str(e)}")
            
            # Move to next relationship
            st.session_state.current_rel_index += 1
            st.experimental_rerun()
    
    with col2:
        if st.button("👎 Reject", key="reject_btn"):
            # Skip this relationship
            st.session_state.current_rel_index += 1
            st.experimental_rerun()