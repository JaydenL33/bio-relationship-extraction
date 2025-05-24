# Bio-Relationship Extraction
A system for extracting and visualizing relationships between bio-medical entities using RAG pipelines, Neo4j graph database, and embeddings-based search.

## Project Overview
Undergraduate thesis at UTS focusing on:
- Extracting relationships between organisms, chemicals, and bio-medical entities from PubMed articles
- Building a graph database to store and query relationships
- Providing a search and visualization interface
- Using local LLMs via Ollama for processing

## Architecture
- **Backend**: FastAPI server with LlamaIndex for RAG pipelines
- **Vector Database**: PostgreSQL with pgvector for document embeddings
- **Graph Database**: Neo4j for storing extracted relationships
- **LLM Integration**: Ollama for local large language model inference
- **Frontend**: Simple web interface for querying and visualization

## Technical Requirements
- Python 3.12 for Backend
- Python 3.11 for Frontend
- Poetry (v2.1.2 or newer)
- Docker and Docker Compose
- NVIDIA GPU with CUDA support (recommended)
- WSL2 for Windows users

### MAC
- Python 3.12
- Poetry (v2.1.2 or newer)
- Docker and Docker Compose

## Setup Instructions
1. **Install Prerequisites**
   - Pyenv (Python version management) although you can just have python3.11 installed, don't have to use Pyenv
   - Poetry
   - Docker
   - Docker Compose
2. **Set up Python environment**
   ```bash
   # Install Poetry if not already installed
   curl -sSL https://install.python-poetry.org | python3 -
   
   # Navigate to project directory
   cd bio-relationship-extraction
   
   # Install dependencies
   poetry install
   
   # Activate the virtual environment
   poetry shell
   ```
3. **Start database services**
   ```bash
   docker-compose up -d
   ```
4. **Configure Application**
   - Update `src/backend/services/llm.py` for Ollama instance
   - Update database configurations if defaults changed

MAKE SURE YOU'RE IN THE VIRTUALENV/POETRY ENV
5. **Start backend server**
   ```bash
   python3 ./main.py
   ```
6. **Start frontend (if applicable)**
   ```bash
   python3 ./main.py
   ```

## Using the Application
- **Search PubMed**: Upload PubMed articles to extract relationships
- **Query Relationships**: Ask about relationships between biological entities
- **Visualize Results**: View and explore extracted relationships
- **API Testing with Postman**: 
  - Import the provided Postman collection from `docs/postman/bio-relationship-api.json`
  - Use Postman to test API endpoints at `http://localhost:8000`
  - Available endpoints include document upload, relationship queries, and entity searches
- **Alternative LLM Options**:
  - While Ollama is recommended for local inference, you can use other models
  - LlamaIndex supports various LLM providers through connectors
  - Simply install the appropriate connector package (e.g., `pip install llama-index-llms-openai`)
  - Modify `src/backend/services/llm.py` to use your preferred model
  - Options include OpenAI, Anthropic, Hugging Face, and many others if you can't run models locally

## Example Queries
- "What metabolites are produced by Starfish"

## Development
### Project Structure
### Data Flow
- Documents retrieved from PubMed or uploaded
- Text embedded and stored in PostgreSQL with pgvector
- LLM extracts relationships using structured output
- Relationships stored in Neo4j as a graph
- User queries processed via RAG pipeline

## License
MIT License - see the LICENSE file for details.

## Authors
Jayden Lee - Graduate @ University of Technology Sydney and Machine Learning Engineer @ AMP
### Get in Contact
Add me on LinkedIn - https://www.linkedin.com/in/jayden-l33/
But please read all of the docs before doing so!
