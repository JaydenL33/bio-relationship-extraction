import time
import requests
from typing import List, Tuple, Set

# Configuration
URL = "http://localhost:8000/questions"  # Replace with your actual backend URL
NUM_RUNS = 5  # Number of times to run each query

# Define queries with expected relationships and thresholds
queries = [
    {
        "text": "What algae produce yessotoxins?",
        "expected_relationships": [
            ("Gonyaulax spinifera", "PRODUCES", "yessotoxins")
        ],
        "threshold": 1
    },
    {
        "text": "Which organisms produce saponins?",
        "expected_relationships": [
            ("starfish", "PRODUCES", "saponins")
        ],
        "threshold": 1
    },
    {
        "text": "What are the ecological effects of starfish saponins?",
        "expected_relationships": [
            ("saponins", "INHIBITS", "marine medaka embryos"),
            ("saponins", "INHIBITS", "predators")
        ],
        "threshold": 1
    },
    {
        "text": "What is the role of saponins in starfish?",
        "expected_relationships": [
            ("starfish", "PRODUCES", "saponins"),
            ("saponins", "INHIBITS", "predators")
        ],
        "threshold": 1
    },
    {
        "text": "What compounds are isolated from red algae?",
        "expected_relationships": [
            ("CcrSULT1", "ISOLATED_FROM", "Chondrus crispus")
        ],
        "threshold": 1
    }
]

def get_relationships(url: str, query_text: str) -> List[Tuple[str, str, str]]:
    """Send a POST request to the backend and extract relationships, normalizing case."""
    query_data = {"text": query_text}
    try:
        response = requests.post(url, json=query_data)
        response.raise_for_status()
        data = response.json()
        # Extract relationships from the first response object, lowercasing all components
        relationships = data[0]["response"]["relationships"]
        return [(rel["entity1"].lower(), rel["relation"].lower(), rel["entity2"].lower()) 
                for rel in relationships]
    except Exception as e:
        print(f"Error in request for '{query_text}': {e}")
        return []

def run_query_multiple_times(url: str, query_text: str, num_runs: int = 5) -> Set[Tuple[str, str, str]]:
    """Run the query multiple times and collect unique relationships."""
    all_relationships = set()
    for run in range(1, num_runs + 1):
        print(f"Running query: '{query_text}', run {run}/{num_runs}")
        relationships = get_relationships(url, query_text)
        print("Sleeping 10 seconds before next run...")
        time.sleep(10)
        all_relationships.update(relationships)
    return all_relationships

def calculate_recall(extracted_set: Set[Tuple[str, str, str]], expected_set: Set[Tuple[str, str, str]]) -> Tuple[float, List[Tuple[str, str, str]], List[Tuple[str, str, str]]]:
    """Calculate recall and identify found/missing relationships, normalizing case."""
    # Normalize case for expected relationships
    expected_set_lower = {(e1.lower(), rel.lower(), e2.lower()) for e1, rel, e2 in expected_set}
    # Normalize case for extracted relationships (already normalized in get_relationships)
    found = expected_set_lower.intersection(extracted_set)
    missing = expected_set_lower - extracted_set
    recall = len(found) / len(expected_set_lower) if expected_set_lower else 0
    return recall, list(found), list(missing)

def main():
    passed_count = 0
    for query in queries:
        query_text = query["text"]
        expected_set = set(query["expected_relationships"])
        threshold = query["threshold"]

        # Collect relationships over multiple runs
        extracted_set = run_query_multiple_times(URL, query_text, NUM_RUNS)

        # Calculate recall and identify found/missing relationships
        recall, found, missing = calculate_recall(extracted_set, expected_set)

        # Determine pass/fail
        pass_fail = "Pass" if recall >= threshold else "Fail"
        if recall >= threshold:
            passed_count += 1

        # Print results
        print(f"\nQuery: {query_text}")
        print(f"Recall: {recall:.2f}")
        print(f"Pass/Fail: {pass_fail}")
        print("Extracted Set Relationships:" + str(extracted_set))
        print("Expected Relationships:" + str(expected_set))

        if missing:
            print("Missing Relationships:")
            for rel in missing:
                print(f"  {rel}")

    # Print summary
    print(f"\nSummary: {passed_count} out of {len(queries)} queries passed.")

if __name__ == "__main__":
    main()