def get_data_from_api(endpoint):
    import requests

    url = f"http://localhost:8000/{endpoint}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()  # Return the JSON response
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to API: {e}")
        return None