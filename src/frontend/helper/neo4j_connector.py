from collections import namedtuple
import random

# Mock Node and Relationship classes for development
class MockNode:
    def __init__(self, id, labels, properties):
        self.id = id
        self.labels = labels
        self.properties = properties
    
    def get(self, key, default=None):
        return self.properties.get(key, default)

class MockRelationship:
    def __init__(self, type):
        self.type = type

# Sample data for knowledge graph visualization
SAMPLE_GRAPH_DATA = [
    {
        'n': MockNode(1, ["Gene"], {"name": "BRCA1"}),
        'r': MockRelationship("ASSOCIATED_WITH"),
        'm': MockNode(2, ["Disease"], {"name": "Breast Cancer"})
    },
    {
        'n': MockNode(3, ["Gene"], {"name": "p53"}),
        'r': MockRelationship("REGULATES"),
        'm': MockNode(4, ["Pathway"], {"name": "Apoptosis"})
    },
    {
        'n': MockNode(5, ["Drug"], {"name": "Metformin"}),
        'r': MockRelationship("TREATS"),
        'm': MockNode(6, ["Disease"], {"name": "Type 2 Diabetes"})
    },
    {
        'n': MockNode(7, ["Protein"], {"name": "IL-6"}),
        'r': MockRelationship("ACTIVATES"),
        'm': MockNode(8, ["Pathway"], {"name": "JAK-STAT Pathway"})
    },
    {
        'n': MockNode(9, ["Drug"], {"name": "Trastuzumab"}),
        'r': MockRelationship("INHIBITS"),
        'm': MockNode(10, ["Protein"], {"name": "HER2"})
    },
    {
        'n': MockNode(11, ["Gene"], {"name": "BRCA2"}),
        'r': MockRelationship("ASSOCIATED_WITH"),
        'm': MockNode(2, ["Disease"], {"name": "Breast Cancer"})
    },
    {
        'n': MockNode(13, ["Gene"], {"name": "TP53"}),
        'r': MockRelationship("ASSOCIATED_WITH"),
        'm': MockNode(14, ["Disease"], {"name": "Lung Cancer"})
    },
    {
        'n': MockNode(15, ["Protein"], {"name": "TNF-alpha"}),
        'r': MockRelationship("ACTIVATES"),
        'm': MockNode(16, ["Pathway"], {"name": "NF-kB Pathway"})
    },
    {
        'n': MockNode(17, ["Drug"], {"name": "Imatinib"}),
        'r': MockRelationship("INHIBITS"),
        'm': MockNode(18, ["Protein"], {"name": "BCR-ABL"})
    },
    {
        'n': MockNode(19, ["Species"], {"name": "H. sapiens"}),
        'r': MockRelationship("EXPRESSES"),
        'm': MockNode(1, ["Gene"], {"name": "BRCA1"})
    }
]

class Neo4jConnector:
    """
    Class to handle connections to Neo4j database (mocked for development)
    """
    
    def __init__(self, uri, user, password):
        """
        Initialize the connector
        
        Args:
            uri (str): Neo4j URI
            user (str): Neo4j username
            password (str): Neo4j password
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
        self.connected = False
    
    def connect(self):
        """
        Establish connection to Neo4j (mocked for development)
        """
        try:
            # For development: mock successful connection
            self.connected = True
            print(f"Connected to Neo4j (mock). Using sample data.")
            return True
        except Exception as e:
            print(f"Error connecting to Neo4j: {e}")
            return False
    
    def close(self):
        """
        Close the Neo4j connection
        """
        self.connected = False
    
    def fetch_data(self, query, params=None):
        """
        Execute a Cypher query and return results (mocked for development)
        
        Args:
            query (str): Cypher query
            params (dict, optional): Query parameters
            
        Returns:
            list: Query results
        """
        if not self.connected:
            print("Not connected to Neo4j")
            return []
        
        try:
            # For development: return mock data based on query content
            if "count(r) as count" in query:
                # For duplicate relationship check
                is_duplicate = random.choice([True, False])
                Record = namedtuple('Record', ['count'])
                return [Record(1 if is_duplicate else 0)]
            
            elif "MATCH (n)-[r]->(m)" in query:
                # For graph visualization
                # Could filter based on entity_type and relationship_type from the query
                if "LIMIT" in query:
                    # Extract limit value
                    limit = int(query.split("LIMIT")[1].strip())
                    return SAMPLE_GRAPH_DATA[:min(limit, len(SAMPLE_GRAPH_DATA))]
                return SAMPLE_GRAPH_DATA
            
            # Default empty result
            return []
            
        except Exception as e:
            print(f"Error executing query: {e}")
            return []