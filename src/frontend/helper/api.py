import requests
import json
import random

API_BASE_URL = "http://localhost:8000/api/v1/"

# Sample data for development
SAMPLE_PAPERS = [
    {
        "id": 1,
        "title": "Effects of BRCA1 and BRCA2 mutations on breast cancer prognosis",
        "authors": "Smith J, Johnson A, Williams B",
        "publication_date": "2020-05-15",
        "journal": "Journal of Cancer Research"
    },
    {
        "id": 2,
        "title": "p53 pathways in lung cancer development",
        "authors": "Chen X, Zhang Y, Anderson P",
        "publication_date": "2019-11-03",
        "journal": "Nature Oncology"
    },
    {
        "id": 3,
        "title": "Metformin use in type 2 diabetes patients",
        "authors": "Brown T, Davis R, Wilson E",
        "publication_date": "2021-02-28",
        "journal": "Diabetes Care"
    },
    {
        "id": 4,
        "title": "IL-6 signaling in autoimmune diseases",
        "authors": "Garcia M, Martinez L, Lopez J",
        "publication_date": "2018-07-12",
        "journal": "Immunology Today"
    },
    {
        "id": 5,
        "title": "HER2 overexpression and trastuzumab response",
        "authors": "Taylor K, Adams S, Nelson R",
        "publication_date": "2022-01-10",
        "journal": "Breast Cancer Research"
    }
]

SAMPLE_RELATIONSHIPS = [
    {
        "id": 1,
        "subject": "BRCA1",
        "subject_type": "Gene",
        "predicate": "ASSOCIATED_WITH",
        "object": "Breast Cancer",
        "object_type": "Disease",
        "context": "Mutations in BRCA1 are strongly associated with an increased risk of breast cancer.",
        "paper_title": "Effects of BRCA1 and BRCA2 mutations on breast cancer prognosis",
        "confidence_score": 0.92
    },
    {
        "id": 2,
        "subject": "p53",
        "subject_type": "Gene",
        "predicate": "REGULATES",
        "object": "Apoptosis",
        "object_type": "Pathway",
        "context": "Wild-type p53 regulates apoptosis through multiple molecular pathways.",
        "paper_title": "p53 pathways in lung cancer development",
        "confidence_score": 0.88
    },
    {
        "id": 3,
        "subject": "Metformin",
        "subject_type": "Drug",
        "predicate": "TREATS",
        "object": "Type 2 Diabetes",
        "object_type": "Disease",
        "context": "Metformin is the first-line treatment for type 2 diabetes in most clinical guidelines.",
        "paper_title": "Metformin use in type 2 diabetes patients",
        "confidence_score": 0.95
    },
    {
        "id": 4,
        "subject": "IL-6",
        "subject_type": "Protein",
        "predicate": "ACTIVATES",
        "object": "JAK-STAT Pathway",
        "object_type": "Pathway",
        "context": "IL-6 activates the JAK-STAT signaling pathway, contributing to inflammation.",
        "paper_title": "IL-6 signaling in autoimmune diseases",
        "confidence_score": 0.87
    },
    {
        "id": 5,
        "subject": "Trastuzumab",
        "subject_type": "Drug",
        "predicate": "INHIBITS",
        "object": "HER2",
        "object_type": "Protein",
        "context": "Trastuzumab specifically inhibits HER2 signaling in breast cancer patients with HER2 overexpression.",
        "paper_title": "HER2 overexpression and trastuzumab response",
        "confidence_score": 0.93
    }
]

def get_data_from_api(endpoint):
    """
    Fetch data from the API (mocked for development)
    
    Args:
        endpoint (str): API endpoint to call
        
    Returns:
        dict: JSON response from the API
    """
    try:
        # For development: return mock data instead of calling actual API
        if "papers/search" in endpoint:
            # Filter papers based on query if provided
            query = endpoint.split("query=")[-1] if "query=" in endpoint else ""
            if query:
                # Simple filtering based on title containing the query
                filtered_papers = [p for p in SAMPLE_PAPERS if query.lower() in p["title"].lower()]
                return filtered_papers
            else:
                return SAMPLE_PAPERS
        
        elif "relationships/extract" in endpoint:
            # Return sample relationships
            return SAMPLE_RELATIONSHIPS
        
        # Fallback to actual API call (should not reach in demo mode)
        response = requests.get(f"{API_BASE_URL}{endpoint}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return {"error": str(e)}

def post_data_to_api(endpoint, data):
    """
    Send data to the API (mocked for development)
    
    Args:
        endpoint (str): API endpoint to call
        data (dict): Data to send
        
    Returns:
        dict: JSON response from the API
    """
    try:
        # For development: mock successful response
        if "relationships/confirm" in endpoint:
            return {"success": True, "message": "Relationship confirmed (mock)"}
        
        # Fallback to actual API call (should not reach in demo mode)
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            headers={"Content-Type": "application/json"},
            data=json.dumps(data)
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error posting data to API: {e}")
        return {"error": str(e)}