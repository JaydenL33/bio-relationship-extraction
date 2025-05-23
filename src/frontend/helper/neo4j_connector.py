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
        self.connected = False
    
    def connect(self):
        """
        Establish connection to Neo4j
        """
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Test the connection
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                if result.single()["test"] == 1:
                    print("Connected to Neo4j successfully.")
                    self.connected = True
                    return True
            return False
        except Exception as e:
            print(f"Error connecting to Neo4j: {e}")
            return False
    
    def close(self):
        """
        Close the Neo4j connection
        """
        if self.driver:
            self.driver.close()
        self.connected = False
    
    def fetch_data(self, query, params=None):
        """
        Execute a Cypher query and return results
        
        Args:
            query (str): Cypher query
            params (dict, optional): Query parameters
            
        Returns:
            list: Query results
        """
        if not self.connected:
            print("Not connected to Neo4j")
            self.connect()
            if not self.connected:
                return []
        
        try:
            with self.driver.session() as session:
                result = session.run(query, params)
                return [record.data() for record in result]
        except Exception as e:
            print(f"Error executing query: {e}")
            return []
    
    def execute_query(self, query, params=None):
        """
        Execute a Cypher query with parameters and return the result.
        
        Args:
            query (str): Cypher query
            params (dict, optional): Query parameters
            
        Returns:
            list: Query results or None if error
        """
        if not self.connected:
            print("Not connected to Neo4j")
            self.connect()
            if not self.connected:
                return None
        
        try:
            with self.driver.session() as session:
                result = session.run(query, params)
                return [record.data() for record in result]
        except Exception as e:
            print(f"Error executing Neo4j query: {str(e)}")
            return None