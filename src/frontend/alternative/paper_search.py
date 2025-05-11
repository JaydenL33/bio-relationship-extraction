def search_papers_page():
    st.header("Search for Scientific Papers")
    
    # Input for search keywords
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
                    
                    # Display papers in a table
                    papers_df = pd.DataFrame(papers)
                    st.dataframe(papers_df[["title", "authors", "publication_date", "journal"]])
                    
                    # Option to process selected papers
                    if st.button("Extract Relationships from Selected Papers"):
                        with st.spinner("Extracting relationships... This may take a minute."):
                            # Call API to extract relationships from the papers
                            paper_ids = papers_df["id"].tolist()
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