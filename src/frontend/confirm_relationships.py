import streamlit as st
import time
from helper.neo4j_connector import Neo4jConnector

def validate_relationships_page(neo4j_connector: Neo4jConnector):
    st.header("Validate Extracted Relationships")

    # Initialize state variables
    if "relationships" not in st.session_state:
        st.session_state.relationships = []
    if "current_rel_index" not in st.session_state:
        st.session_state.current_rel_index = 0
    if "confirmed_relationships" not in st.session_state:
        st.session_state.confirmed_relationships = []
    if "action" not in st.session_state:
        st.session_state.action = None
    if "return_to_main" not in st.session_state:
        st.session_state.return_to_main = False

    # Handle actions
    if st.session_state.action == "confirm":
        _process_confirmation(neo4j_connector)
        st.session_state.action = None
    elif st.session_state.action == "reject":
        st.session_state.current_rel_index += 1
        st.session_state.result_notification = {
            "success": True,
            "message": "Relationship rejected.",
            "time": time.time()
        }
        st.session_state.action = None
    elif st.session_state.action == "skip":
        st.session_state.current_rel_index += 1
        st.session_state.action = None
    elif st.session_state.action == "start_over":
        st.session_state.current_rel_index = 0
        st.session_state.action = None

    # Handle notification
    if "result_notification" in st.session_state and st.session_state.result_notification:
        if st.session_state.result_notification["success"]:
            st.success(st.session_state.result_notification["message"])
        else:
            st.error(st.session_state.result_notification["message"])
        if time.time() - st.session_state.result_notification["time"] > 3:
            st.session_state.result_notification = None

    # Check for relationships
    if len(st.session_state.relationships) == 0:
        st.info("No relationships to validate. Please search for papers and extract relationships first.")
        return

    total_rels = len(st.session_state.relationships)
    current_index = st.session_state.current_rel_index
    st.progress(float(current_index) / total_rels)
    st.write(f"Reviewing relationship {current_index + 1} of {total_rels}")

    # Check if validation is complete
    if current_index >= total_rels:
        st.success("All relationships have been validated!")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Start Over"):
                st.session_state.action = "start_over"
                st.rerun()
        with col2:
            if st.button("Back to Main Menu"):
                st.session_state.return_to_main = True  # Signal to return to Paper Management
                st.rerun()
        return

    # Get the current relationship to validate
    current_rel = st.session_state.relationships[current_index]

    # Validate current relationship has all required fields
    required_fields = ['subject', 'subject_type', 'predicate', 'object', 'object_type']
    is_valid = all(field in current_rel for field in required_fields)

    if not is_valid:
        st.error("The current relationship is missing required fields.")
        st.write("Relationship data:", current_rel)
        if st.button("Skip Invalid Relationship"):
            st.session_state.action = "skip"
            st.rerun()
        return

    # Display the relationship card
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
        paper_title = current_rel.get('paper_title', 'Unknown Paper')
        context = current_rel.get('context', 'No context provided')
        st.markdown(f"**Source Paper**: {paper_title}")
        st.markdown(f"**Excerpt**: \"{context}\"")

    # Buttons for validation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Confirm", key="confirm_btn"):
            st.session_state.action = "confirm"
            st.rerun()
    with col2:
        if st.button("👎 Reject", key="reject_btn"):
            st.session_state.action = "reject"
            st.rerun()

def _process_confirmation(neo4j_connector):
    try:
        current_rel = st.session_state.relationships[st.session_state.current_rel_index]
        subject = current_rel['subject']
        object_entity = current_rel['object']
        subject_type = current_rel['subject_type']
        object_type = current_rel['object_type']
        predicate = current_rel['predicate']
        paper_title = current_rel.get('paper_title', 'Unknown Paper')
        context = current_rel.get('context', 'No context provided')

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

        result = neo4j_connector.execute_query(query, params)
        success = result is not None and len(result) > 0

        # Store the last confirmed relationship for the details page
        if success:
            st.session_state.last_confirmed_relationship = current_rel
            st.session_state.confirmed_relationships.append(current_rel)
            st.session_state.current_rel_index += 1
            
            # Set flag to show relationship details page
            st.session_state.show_relationship_details = True
        else:
            st.session_state.result_notification = {
                "success": False,
                "message": "Failed to add relationship to the knowledge graph.",
                "time": time.time()
            }

    except Exception as e:
        st.session_state.result_notification = {
            "success": False,
            "message": f"Error adding relationship: {str(e)}",
            "time": time.time()
        }