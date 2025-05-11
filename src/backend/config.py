from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Neo4j Connection Parameters
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

def get_neo4j_connection():
    """
    Establishes and returns a connection to the Neo4j database.
    
    Returns:
        driver: Neo4j driver instance for database operations
    """
    try:
        driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )
        # Verify connection
        with driver.session() as session:
            session.run("RETURN 1")
        print("Neo4j connection established successfully")
        return driver
    except Exception as e:
        print(f"Failed to connect to Neo4j: {e}")
        raise
