import re
import urllib.request
from time import sleep
import json
import uuid

def extract_metadata(abstract_text, pmid):
    """Extract metadata from a single abstract text."""
    study = {
        "id": str(uuid.uuid4()),
        "pmid": pmid,
        "journal": "",
        "title": "",
        "authors": [],
        "author_info": [],
        "abstract": "",
        "key_points": [],
        "doi": ""
    }
    
    # Extract journal (first line, typically journal citation)
    journal_match = re.match(r'([^\n]+)\n', abstract_text)
    if journal_match:
        study["journal"] = journal_match.group(1).strip()
    
    # Extract title (after journal, before authors)
    title_match = re.search(r'\n\n([^\n]+)\n\n', abstract_text)
    if title_match:
        study["title"] = title_match.group(1).strip()
    
    # Extract authors (line before "Author information:")
    authors_match = re.search(r'\n\n([^\n]+)\n\nAuthor information:', abstract_text)
    if authors_match:
        authors_line = authors_match.group(1).strip()
        study["authors"] = [author.strip() for author in authors_line.split(',')]
    
    # Extract author information (between "Author information:" and abstract)
    author_info_match = re.search(r'Author information:\n((?:\(.*?\)[^\n]*\n)+)', abstract_text)
    if author_info_match:
        author_info_lines = author_info_match.group(1).strip().split('\n')
        study["author_info"] = [line.strip() for line in author_info_lines]
    
    # Extract abstract (main text after author info, before metadata like © or DOI)
    abstract_match = re.search(r'Author information:.*?\n\n(.+?)(?=\n\n(?:©|DOI|Conflict of interest))', abstract_text, re.DOTALL)
    if abstract_match:
        study["abstract"] = abstract_match.group(1).strip()
    
    # Extract DOI
    doi_match = re.search(r'DOI: (10\.\d{4}/[^\s]+)', abstract_text)
    if doi_match:
        study["doi"] = doi_match.group(1).strip()
    
    # Generate key points by summarizing abstract
    sentences = study["abstract"].split('. ')
    key_points = []
    for sentence in sentences:
        if any(keyword in sentence.lower() for keyword in [
            'study', 'investigate', 'find', 'result', 'show', 'demonstrate', 
            'implication', 'role', 'effect', 'compare', 'observe', 'develop'
        ]):
            key_points.append(sentence.strip() + ('.' if not sentence.endswith('.') else ''))
    study["key_points"] = key_points[:5]  # Limit to 5 key points
    
    return study

def save_to_json(data, pmid):
    """Save metadata to an individual JSON file named by PMID."""
    filename = f"./documents/{pmid}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def main():
    # User inputs
    query = input("Enter the query keywords such as 'cyanobacteria' to bulk download abstracts? Enter your keyword(s): ")
    query2 = input("How many abstracts you need to download?: ")

    # Replace spaces with %20 for PubMed search
    query = query.replace(" ", "%20")

    # Common settings
    base_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    db = 'db=pubmed'

    # Esearch settings
    search_eutil = 'esearch.fcgi?'
    search_term = '&term=' + query
    search_usehistory = '&usehistory=y'
    search_rettype = '&rettype=xml'  # Explicitly set to XML

    # Call esearch
    search_url = base_url + search_eutil + db + search_term + search_usehistory + search_rettype
    print("Esearch command:\n" + search_url + "\n")
    try:
        f = urllib.request.urlopen(search_url)
        search_data = f.read().decode('utf-8')
    except urllib.error.URLError as e:
        print(f"Error fetching esearch data: {e}")
        return

    # Debug: Print raw search data
    print("Raw esearch response:\n", search_data, "\n")

    # Parse XML response
    try:
        # Extract total abstract count
        count_match = re.findall(r'<Count>(\d+)</Count>', search_data)
        if not count_match:
            print("No abstracts found or unable to parse <Count> from response.")
            return
        total_abstract_count = int(count_match[0])

        # Extract PMIDs
        pmid = re.findall(r'<Id>(\d+)</Id>', search_data)
        if not pmid:
            print("No PMIDs found in response.")
            return

        # Extract WebEnv and QueryKey
        webenv_match = re.findall(r'<WebEnv>(\S+)</WebEnv>', search_data)
        querykey_match = re.findall(r'<QueryKey>(\d+)</QueryKey>', search_data)
        if not webenv_match or not querykey_match:
            print("Unable to parse WebEnv or QueryKey from response.")
            return
        webenv = webenv_match[0]
        querykey = querykey_match[0]
    except Exception as e:
        print(f"Error parsing esearch XML: {e}")
        return

    print("Total abstracts available = ", total_abstract_count)
    print("Type of pmid = ", type(pmid))
    print("Len of pmid = ", len(pmid))
    print("First abstract ID = ", pmid[0] if pmid else "None")

    # Efetch settings
    fetch_eutil = 'efetch.fcgi?'
    retmax = 5
    retstart = 0
    fetch_retmode = "&retmode=text"
    fetch_rettype = "&rettype=abstract"
    fetch_webenv = f"&WebEnv={webenv}"
    fetch_querykey = f"&query_key={querykey}"

    # Fetch abstracts
    all_abstracts = []
    loop_counter = 1

    while True:
        print("Efetch number " + str(loop_counter))
        loop_counter += 1
        fetch_retstart = "&retstart=" + str(retstart)
        fetch_retmax = "&retmax=" + str(retmax)
        fetch_url = base_url + fetch_eutil + db + fetch_querykey + fetch_webenv + fetch_retstart + fetch_retmax + fetch_retmode + fetch_rettype
        print(fetch_url)

        # Fetch data
        try:
            f = urllib.request.urlopen(fetch_url)
            fetch_data = f.read().decode('utf-8')
        except urllib.error.URLError as e:
            print(f"Error fetching efetch data: {e}")
            break

        # Split into individual abstracts
        abstracts = fetch_data.split("\n\n\n")
        all_abstracts.extend(abstracts)

        # Extract metadata for each abstract
        for i, abstract in enumerate(abstracts):
            if abstract.strip():
                # Calculate the index in pmid list
                current_index = retstart + i
                if current_index < len(pmid):
                    current_pmid = pmid[current_index]
                    metadata = extract_metadata(abstract, current_pmid)
                    
                    # Save abstract to text file
                    abs_fields = abstract.split("\n\n")
                    if len(abs_fields) > 4:
                        path_to_write_text = f"./documents/{current_pmid}.txt"
                        with open(path_to_write_text, "w", encoding='utf-8') as fp_text:
                            fp_text.write(abs_fields[4].replace("\n", ""))
                    
                    # Save metadata to individual JSON file
                    save_to_json(metadata, current_pmid)

        print("A total of " + str(len(all_abstracts)) + " abstracts have been downloaded.\n")
        if len(all_abstracts) >= int(query2) or retstart + retmax > total_abstract_count:
            break

        sleep(5)  # Avoid rate limiting
        retstart += retmax

    print(f"Downloaded {len(all_abstracts)} abstracts and saved metadata to individual JSON files.")

if __name__ == '__main__':
    main()