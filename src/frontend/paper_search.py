import streamlit as st
import pandas as pd
from helper.api import get_data_from_api, post_data_to_api

def search_papers_page():
    st.header("Scientific Paper Knowledge Base")
    
    # Initialize session state for selected papers and search results
    if "selected_papers" not in st.session_state:
        st.session_state.selected_papers = []
    if "search_results" not in st.session_state:
        st.session_state.search_results = []
    if "mode" not in st.session_state:
        st.session_state.mode = None
    
    # Display the main mode selection if no mode is currently selected
    if st.session_state.mode is None:
        st.subheader("Choose an Option")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📚 Search Existing Papers", use_container_width=True):
                st.session_state.mode = "search_existing"
                st.rerun()
        
        with col2:
            if st.button("🔍 Download New Papers", use_container_width=True):
                st.session_state.mode = "download_new"
                st.rerun()
        
        # Add an explanation of the workflow
        st.markdown("---")
        st.markdown("""
        ### How it works:
        
        **Search Existing Papers**: Query papers already in our database to find relevant information.
        
        **Download New Papers**: Search PubMed for new papers and add them to our knowledge base.
        
        After selecting papers through either method, you can extract relationships to build the knowledge graph.
        """)
        
        # Return early if no mode is selected
        return
    
    # Show a way to go back to mode selection
    if st.button("← Back to Main Options"):
        st.session_state.mode = None
        st.rerun()
    
    # Display currently selected papers if any
    if st.session_state.selected_papers:
        st.subheader("Selected Papers")
        selected_df = pd.DataFrame(st.session_state.selected_papers)
        st.dataframe(selected_df[["title", "authors", "journal"]])
        
        if st.button("Clear Selected Papers"):
            st.session_state.selected_papers = []
            st.rerun()
        
        # Show extract relationships button if papers are selected
        if st.button("Extract Relationships from Selected Papers"):
            with st.spinner("Extracting relationships... This may take a minute."):
                try:
                    # Call API to extract relationships from the selected papers
                    paper_ids = [paper["id"] for paper in st.session_state.selected_papers]
                    extracted_relationships = get_data_from_api(
                        f"relationships/extract?paper_ids={','.join(map(str, paper_ids))}"
                    )
                    
                    # Store the extracted relationships in session state
                    if extracted_relationships:
                        st.session_state.relationships = extracted_relationships
                        st.session_state.current_rel_index = 0
                        
                        # Display relationships in a table for preview
                        st.subheader(f"Extracted Relationships ({len(extracted_relationships)})")
                        relationships_df = pd.DataFrame([
                            {
                                "Subject": rel["subject"], 
                                "Relationship": rel["predicate"], 
                                "Object": rel["object"]
                            } for rel in extracted_relationships
                        ])
                        st.dataframe(relationships_df, use_container_width=True)
                        
                        st.success(f"Extracted {len(extracted_relationships)} potential relationships.")
                        st.info("Go to 'Validate Relationships' to review and confirm these relationships.")
                    else:
                        st.error("Failed to extract relationships. Check API connection.")
                except Exception as e:
                    st.error(f"Error connecting to API: {str(e)}")
                    st.info("Please ensure the backend API is running.")
    
    # SEARCH EXISTING PAPERS MODE
    if st.session_state.mode == "search_existing":
        st.subheader("Ask Questions About the Knowledge Base")
        st.markdown("Send a question to the LLM to extract relationships from existing papers.")
        
        # Input for search keywords
        search_query = st.text_input("Enter a question for the LLM:", 
                                 placeholder="e.g., What is the relationship of Starfish?")
        
        # Search button
        if st.button("Ask Question"):
            if search_query:
                with st.spinner("Processing your question..."):
                    try:
                        # Send the question to the API endpoint
                        response = post_data_to_api("questions/", {
                            "text": search_query
                        })
                        
                        # Check if we got a valid response
                        if response and isinstance(response, list) and len(response) > 0:
                            # Extract the LLM answer and relationships
                            llm_answer = response[0].get("response", {})
                            relationships = llm_answer.get("relationships", [])
                            explanation = llm_answer.get("explanation", "No explanation provided.")
                            sources = response[0].get("sources", [])
                            
                            # Display the explanation to the user
                            st.subheader("Answer")
                            st.write(explanation)
                            
                            # Format and display the extracted relationships
                            if relationships and len(relationships) > 0:
                                st.subheader(f"Extracted Relationships ({len(relationships)})")
                                
                                # Convert relationships to the format our system uses
                                formatted_relationships = []
                                for rel in relationships:
                                    formatted_rel = {
                                        'subject': rel.get('entity1', ''),
                                        'subject_type': 'Entity',  # Default type if not specified
                                        'predicate': rel.get('relation', 'RELATED_TO'),
                                        'object': rel.get('entity2', ''),
                                        'object_type': 'Entity',  # Default type if not specified
                                        'context': explanation,
                                        'paper_title': f"Generated from question: {search_query}"
                                    }
                                    formatted_relationships.append(formatted_rel)
                                st.info("Please go to the **Validate Relationships** tab in the sidebar to review these relationships.")
                                # Display relationships in a table for preview
                                relationships_df = pd.DataFrame([
                                    {
                                        "Subject": rel["subject"], 
                                        "Relationship": rel["predicate"], 
                                        "Object": rel["object"]
                                    } for rel in formatted_relationships
                                ])
                                st.dataframe(relationships_df, use_container_width=True)
                                
                                # Store the relationships for validation and direct user to confirmation page
                                st.session_state.relationships = formatted_relationships
                                st.session_state.current_rel_index = 0
                                
                                # Display source documents if available before redirecting
                                if sources and len(sources) > 0:
                                    st.subheader("Source Documents")
                                    for i, source in enumerate(sources):
                                        if "node" in source and "text" in source["node"]:
                                            extra_info = source["node"].get("extra_info", {})
                                            title = extra_info.get("title", "Untitled Paper")
                                            with st.expander(f"Source: {title} | Score: {float(source['score']):.2f}"):
                                                # Display metadata in a structured way
                                                st.markdown(f"**Title**: {extra_info.get('title', 'Unknown')}")
                                                st.markdown(f"**Authors**: {extra_info.get('authors', 'Unknown')}")
                                                st.markdown(f"**Journal**: {extra_info.get('journal', 'Unknown')}")
                                                st.markdown(f"**PMID**: {extra_info.get('pmid', 'Unknown')}")
                                                st.markdown(f"**DOI**: {extra_info.get('doi', 'Unknown')}")
                                                st.markdown(f"**SCORE**: {float(source['score']):.2f}")
                                                st.markdown("---")
                                                st.markdown("**Content:**")
                                                st.markdown(source["node"]["text"])
                                
                                # Remove auto-redirect
                                # st.session_state.redirect_to_validate = True
                                # st.rerun()
                            else:
                                st.warning("No relationships were extracted from the response.")
                            
                            # Display source documents if available if no relationships were found
                            if (not relationships or len(relationships) == 0) and sources and len(sources) > 0:
                                st.subheader("Source Documents")
                                for i, source in enumerate(sources):
                                    if "node" in source and "text" in source["node"]:
                                        extra_info = source["node"].get("extra_info", {})
                                        title = extra_info.get("title", "Untitled Paper")
                                        with st.expander(f"Source: {title} | Score: {float(source['score']):.2f}"):
                                            # Display metadata in a structured way
                                            st.markdown(f"**Title**: {extra_info.get('title', 'Unknown')}")
                                            st.markdown(f"**Authors**: {extra_info.get('authors', 'Unknown')}")
                                            st.markdown(f"**Journal**: {extra_info.get('journal', 'Unknown')}")
                                            st.markdown(f"**PMID**: {extra_info.get('pmid', 'Unknown')}")
                                            st.markdown(f"**DOI**: {extra_info.get('doi', 'Unknown')}")
                                            st.markdown("---")
                                            st.markdown("**Content:**")
                                            st.markdown(source["node"]["text"])
                        else:
                            st.error("Failed to get a valid response from the API.")
                    except Exception as e:
                        st.error(f"Error connecting to API: {str(e)}")
                        st.info("Please ensure the backend API is running.")
            else:
                st.warning("Please enter a question.")
    
    # DOWNLOAD NEW PAPERS MODE
    elif st.session_state.mode == "download_new":
        st.subheader("Download New Papers from PubMed")
        st.markdown("Search PubMed for new papers and add them to our knowledge base.")
        
        # Input for search keywords
        search_query = st.text_input("Enter keywords to search PubMed:", 
                                 placeholder="e.g., cancer immunotherapy, alzheimer's disease")
        
        # Options for download
        max_papers = st.slider("Maximum number of papers to download", min_value=1, max_value=10, value=5)
        
        # Search button
        if st.button("Search PubMed"):
            if search_query:
                # Call API to search for papers
                with st.spinner("Searching PubMed and downloading papers..."):
                    try:
                        # Use the PubMed search API endpoint
                        response = post_data_to_api("pubmed/search/", {
                            "query": search_query,
                            "max_documents": max_papers
                        })
                        
                        if response and response.get("status") == "success":
                            st.success(f"Downloaded and indexed {response.get('document_count')} papers.")
                    except Exception as e:
                        st.error(f"Error connecting to API: {str(e)}")
                        st.info("Please ensure the backend API is running.")
            else:
                st.warning("Please enter search keywords.")
    
    # Display search results and paper selection options (common to both modes)
    if st.session_state.search_results:
        st.subheader("Search Results")
        
        # Define a function to handle paper selection
        def update_selection(paper_id, is_selected):
            if is_selected:
                # Add paper to selected papers if not already there
                if not any(p["id"] == paper_id for p in st.session_state.selected_papers):
                    paper = next((p for p in st.session_state.search_results if p["id"] == paper_id), None)
                    if paper:
                        st.session_state.selected_papers.append(paper)
            else:
                # Remove paper from selected papers
                st.session_state.selected_papers = [
                    p for p in st.session_state.selected_papers if p["id"] != paper_id
                ]
        
        # Create selection states if they don't exist
        if "paper_selections" not in st.session_state:
            st.session_state.paper_selections = {}
        
        # Initialize selection state for each paper
        for paper in st.session_state.search_results:
            paper_id = paper["id"]
            if paper_id not in st.session_state.paper_selections:
                # Check if paper is already in selected papers
                st.session_state.paper_selections[paper_id] = any(
                    p["id"] == paper_id for p in st.session_state.selected_papers
                )
        
        # Display papers with selection checkboxes
        for i, paper in enumerate(st.session_state.search_results):
            paper_id = paper["id"]
            col1, col2 = st.columns([0.1, 0.9])
            
            with col1:
                # Create a unique key for each checkbox
                checkbox_key = f"paper_{paper_id}_{i}"
                
                # Get current selection state
                current_selection = st.session_state.paper_selections.get(paper_id, False)
                
                # Display checkbox
                if st.checkbox("", value=current_selection, key=checkbox_key, 
                              on_change=update_selection, args=(paper_id, not current_selection)):
                    # Update selection state (this will be called when checkbox changes)
                    st.session_state.paper_selections[paper_id] = True
                else:
                    st.session_state.paper_selections[paper_id] = False
            
            with col2:
                st.markdown(f"**{paper['title']}**")
                st.markdown(f"*{paper['authors']}* - {paper['journal']} ({paper['publication_date']})")
                st.markdown("---")
        
        # Button to select all papers
        if st.button("Select All Papers"):
            for paper in st.session_state.search_results:
                update_selection(paper["id"], True)
            # Update selection states
            for paper_id in st.session_state.paper_selections:
                st.session_state.paper_selections[paper_id] = True
            st.rerun()