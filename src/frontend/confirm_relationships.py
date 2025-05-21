import streamlit as st
import time

def validate_relationships_page(neo4j_connector):
    st.header("Validate Extracted Relationships")
    
    # Success/Error notification area at top
    if "result_notification" in st.session_state:
        if st.session_state.result_notification["success"]:
            st.success(st.session_state.result_notification["message"])
        else:
            st.error(st.session_state.result_notification["message"])
        
        # Clear the notification after 3 seconds
        if time.time() - st.session_state.result_notification["time"] > 3:
            del st.session_state.result_notification
    
    # Check if we have relationships to validate
    if "relationships" not in st.session_state or len(st.session_state.relationships) == 0:
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
    
    # Buttons for validation
    col1, col2 = st.columns(2)
    
    def confirm_relationship():
        try:
            subject = current_rel['subject']
            object_entity = current_rel['object']
            subject_type = current_rel['subject_type'] 
            object_type = current_rel['object_type']
            predicate = current_rel['predicate']
            
            # Format the parameters for Neo4j
            query = """
            MERGE (s:{subject_type} {{name: $subject}})
            MERGE (o:{object_type} {{name: $object}})
            MERGE (s)-[r:{predicate}]->(o)
            ON CREATE SET r.created = timestamp(), r.context = $context, r.source = $paper_title
            ON MATCH SET r.updated = timestamp(), r.context = $context, r.source = $paper_title
            RETURN s, r, o
            """.format(
                subject_type=subject_type,
                object_type=object_type,
                predicate=predicate
            )
            
            params = {
                "subject": subject,
                "object": object_entity,
                "context": context,
                "paper_title": paper_title
            }
            
            # Execute the query and save result flag
            result = neo4j_connector.execute_query(query, params)
            success = result is not None and len(result) > 0
            
            # Set notification state
            st.session_state.result_notification = {
                "success": success,
                "message": "Relationship confirmed and added to the knowledge graph!" if success else "Failed to add relationship to the knowledge graph.",
                "time": time.time()
            }
            
            # Store the confirmed relationship
            if "confirmed_relationships" not in st.session_state:
                st.session_state.confirmed_relationships = []
            
            if success:
                st.session_state.confirmed_relationships.append(current_rel)
            
            # Move to the next relationship
            st.session_state.current_rel_index += 1
            
        except Exception as e:
            # Set error notification state
            st.session_state.result_notification = {
                "success": False,
                "message": f"Error adding relationship: {str(e)}",
                "time": time.time()
            }
    
    with col1:
        if st.button("👍 Confirm", key="confirm_btn", on_click=confirm_relationship):
            pass  # The actual logic is in the confirm_relationship function
    
    with col2:
        if st.button("👎 Reject", key="reject_btn"):
            # Skip this relationship
            st.session_state.current_rel_index += 1
            # Set notification state
            st.session_state.result_notification = {
                "success": True,
                "message": "Relationship rejected.",
                "time": time.time()
            }
            st.rerun()