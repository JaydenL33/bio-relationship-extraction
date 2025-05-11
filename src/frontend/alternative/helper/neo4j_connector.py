from neo4j import GraphDatabase

class Neo4jConnector:
    """
    Class to handle connections to Neo4j database
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
    
    def connect(self):
        """
        Establish connection to Neo4j
        """
        try:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password)
            )
            # Test connection
            with self.driver.session() as session:
                result = session.run("MATCH (n) RETURN count(n) as count")
                count = result.single()["count"]
                print(f"Connected to Neo4j. Database contains {count} nodes.")
            return True
        except Exception as e:
            print(f"Error connecting to Neo4j: {e}")
            return False
    
    def close(self):
        """
        Close the Neo4j connection
        """
        if self.driver:
            self.driver.close()
    
    def fetch_data(self, query, params=None):
        """
        Execute a Cypher query and return the results
        
        Args:
            query (str): Cypher query
            params (dict, optional): Query parameters
            
        Returns:
            list: Query results
        """
        if not self.driver:
            print("Not connected to Neo4j")
            return []
        
        try:
            with self.driver.session() as session:
                result = session.run(query, params or {})
                return [record for record in result]
        except Exception as e:
            print(f"Error executing query: {e}")
            return []