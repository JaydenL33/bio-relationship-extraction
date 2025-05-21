import streamlit as st
import pandas as pd
from helper.api import get_data_from_api

def search_papers_page():
    st.header("Search for Scientific Papers")
    
    # Initialize session state for selected papers and search results
    if "selected_papers" not in st.session_state:
        st.session_state.selected_papers = []
    if "search_results" not in st.session_state:
        st.session_state.search_results = []
    
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
    st.subheader("Search for Papers")
    search_query = st.text_input("Enter keywords to search for papers:", 
                               placeholder="e.g., cancer immunotherapy, alzheimer's disease")
    
    # Search button
    if st.button("Search") and search_query:
        # Call API to search for papers
        with st.spinner("Searching for papers..."):
            try:
                papers = get_data_from_api(f"papers/search?query={search_query}")
                
                if not papers or len(papers) == 0:
                    st.warning("No papers found for your search query.")
                    st.session_state.search_results = []
                else:
                    st.success(f"Found {len(papers)} papers.")
                    # Store search results in session state
                    st.session_state.search_results = papers
            except Exception as e:
                st.error(f"Error connecting to API: {str(e)}")
                st.info("Please ensure the backend API is running.")
    
    # Display search results and paper selection options
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
            st.experimental_rerun()