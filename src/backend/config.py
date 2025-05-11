from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_neo4j_connection():
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "Neo4jTestPassword"
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        return driver
    except Exception as e:
        raise Exception(f"Failed to connect to Neo4j: {str(e)}")
