# Streamlit Neo4J API App

This project is a Streamlit application that connects to a REST API running on localhost:8000 and retrieves data from a Neo4J database. The application provides an interactive interface for users to visualize and interact with the data.

## Project Structure

```
python-streamlit-neo4j-api-app
├── app.py                # Main entry point of the Streamlit application
├── utils                 # Utility functions for API and database connections
│   ├── api_connector.py  # Functions to connect to the API
│   └── db_connector.py   # Functions to connect to the Neo4J database
├── config.py             # Configuration settings for API and database
├── requirements.txt      # List of dependencies
└── README.md             # Documentation for the project
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd python-streamlit-neo4j-api-app
   ```

2. **Install the required packages:**
   Make sure you have Python installed, then run:
   ```
   poetry env activate
   poetry install
   ```

3. **Configure the application:**
   Update the `config.py` file with your Neo4J database credentials and API endpoint if necessary.

4. **Run the application:**
   Start the Streamlit app by executing:
   ```
   streamlit run app.py
   ```

## Usage

Once the application is running, you can access it in your web browser at `http://localhost:8501`. The app will connect to the API and Neo4J database to fetch and display data.

## API and Database Connections

- The application connects to a REST API hosted on `http://localhost:8000`. Ensure that the API is running before starting the Streamlit app.
- The Neo4J database connection is managed through the `Neo4jConnector` class in `utils/db_connector.py`. Make sure the database is accessible with the credentials provided in `config.py`.

## Dependencies

This project requires the following Python packages:

- Streamlit
- Requests
- Neo4J Python Driver

