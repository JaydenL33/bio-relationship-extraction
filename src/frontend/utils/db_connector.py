class Neo4jConnector:
    def __init__(self, uri, user, password):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None

    def connect(self):
        from neo4j import GraphDatabase
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def fetch_data(self, query):
        with self.driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]

    def close(self):
        if self.driver is not None:
            self.driver.close()