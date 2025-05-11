import streamlit as st
import pandas as pd
from helper.api import get_data_from_api

def search_papers_page():
    st.header("Search for Scientific Papers")
    
    # Initialize session state for selected papers if it doesn't exist
    if "selected_papers" not in st.session_state:
        st.session_state.selected_papers = []
    
    # Display currently selected papers if any
    if st.session_state.selected_papers:
        st.subheader("Selected Papers")
        selected_df = pd.DataFrame(st.session_state.selected_papers)
        st.dataframe(selected_df[["title", "authors", "journal"]])
        
        if st.button("Clear Selected Papers"):
            st.session_state.selected_papers = []
            st.experimental_rerun()
        
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
                    st.session_state.relationships = extracted_relationships
                    st.session_state.current_rel_index = 0
                    
                    st.success(f"Extracted {len(extracted_relationships)} potential relationships.")
                    st.info("Go to 'Validate Relationships' to review and confirm these relationships.")
                except Exception as e:
                    st.error(f"Error connecting to API: {str(e)}")
                    st.info("Please ensure the backend API is running.")
    
    # Input for search keywords
    st.subheader("Search for More Papers")
    search_query = st.text_input("Enter keywords to search for papers:", 
                               placeholder="e.g., cancer immunotherapy, alzheimer's disease")
    
    if st.button("Search") and search_query:
        # Call API to search for papers
        with st.spinner("Searching for papers..."):
            try:
                papers = get_data_from_api(f"papers/search?query={search_query}")
                
                if not papers or len(papers) == 0:
                    st.warning("No papers found for your search query.")
                else:
                    st.success(f"Found {len(papers)} papers.")
                    
                    # Create a container for the search results
                    with st.container():
                        st.subheader("Search Results")
                        
                        # Convert papers to DataFrame for display
                        papers_df = pd.DataFrame(papers)
                        
                        # Create checkboxes for paper selection
                        for i, paper in enumerate(papers):
                            col1, col2 = st.columns([0.1, 0.9])
                            with col1:
                                # Check if paper is already selected
                                is_selected = any(p["id"] == paper["id"] for p in st.session_state.selected_papers)
                                # Create a unique key for each checkbox
                                checkbox_key = f"paper_{paper['id']}_{i}"
                                if st.checkbox("", value=is_selected, key=checkbox_key):
                                    # Add to selected papers if not already there
                                    if not is_selected:
                                        st.session_state.selected_papers.append(paper)
                                else:
                                    # Remove from selected papers if it was there
                                    if is_selected:
                                        st.session_state.selected_papers = [
                                            p for p in st.session_state.selected_papers if p["id"] != paper["id"]
                                        ]
                            
                            with col2:
                                st.markdown(f"**{paper['title']}**")
                                st.markdown(f"*{paper['authors']}* - {paper['journal']} ({paper['publication_date']})")
                                st.markdown("---")
                        
                        # Button to add all displayed papers to selection
                        if st.button("Select All Displayed Papers"):
                            # Add all papers that aren't already selected
                            for paper in papers:
                                if not any(p["id"] == paper["id"] for p in st.session_state.selected_papers):
                                    st.session_state.selected_papers.append(paper)
                            st.experimental_rerun()
            except Exception as e:
                st.error(f"Error connecting to API: {str(e)}")
                st.info("Please ensure the backend API is running.")