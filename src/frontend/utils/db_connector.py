"""
Compatibility layer to redirect to helper.neo4j_connector
This maintains backward compatibility with any code that might import from utils.db_connector
"""

from helper.neo4j_connector import Neo4jConnector as BaseNeo4jConnector

class Neo4jConnector(BaseNeo4jConnector):
    """
    Neo4j connector class - redirects to implementation in helper.neo4j_connector
    This class is kept for backward compatibility
    """
    pass