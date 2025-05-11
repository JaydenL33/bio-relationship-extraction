import streamlit as st
import requests
from utils.api_connector import get_data_from_api
from utils.db_connector import Neo4jConnector
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

def main():
    st.title("Streamlit App with Neo4J and API")

    # Connect to the Neo4J database
    neo4j_connector = Neo4jConnector(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    neo4j_connector.connect()

    # Fetch data from the API
    api_data = get_data_from_api("health")

    # Display API data
    st.subheader("Data from API")
    st.write(api_data)

    # Fetch data from Neo4J
    neo4j_data = neo4j_connector.fetch_data("MATCH (n) RETURN n LIMIT 10")

    # Display Neo4J data
    st.subheader("Data from Neo4J")
    st.write(neo4j_data)

    # Close the Neo4J connection
    neo4j_connector.close()

if __name__ == "__main__":
    main()