import requests
import json

API_BASE_URL = "http://localhost:8000/api/v1/"

def get_data_from_api(endpoint):
    """
    Fetch data from the API
    
    Args:
        endpoint (str): API endpoint to call
        
    Returns:
        dict: JSON response from the API
    """
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return {"error": str(e)}

def post_data_to_api(endpoint, data):
    """
    Send data to the API
    
    Args:
        endpoint (str): API endpoint to call
        data (dict): Data to send
        
    Returns:
        dict: JSON response from the API
    """
    try:
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