from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel, Field
import re
import urllib.request
from time import sleep
import os

from services.initalise_vector_store import upload_documents

router = APIRouter()

class PubmedSearchRequest(BaseModel):
    query: str = Field(..., description="Keywords to search for in PubMed")
    max_documents: int = Field(10, description="Maximum number of documents to download (max 10)")

@router.post("/pubmed/search/")
async def search_pubmed(request: PubmedSearchRequest = Body(...)):
    # Ensure max_documents is limited to 10
    if request.max_documents > 10:
        request.max_documents = 10
    
    query = request.query.replace(" ", "%20")
    
    # Create a temporary directory for downloaded documents
    documents_dir = "./documents"
    os.makedirs(documents_dir, exist_ok=True)
    
    # PubMed API settings
    base_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    db = 'db=pubmed'
    
    # esearch settings
    search_eutil = 'esearch.fcgi?'
    search_term = '&term=' + query
    search_usehistory = '&usehistory=y'
    search_rettype = '&rettype=json'
    
    try:
        # Call the esearch command
        search_url = base_url + search_eutil + db + search_term + search_usehistory + search_rettype
        f = urllib.request.urlopen(search_url)
        search_data = f.read().decode('utf-8')
        
        # Extract abstract count and PMIDs
        total_abstract_count = int(re.findall("<Count>(\d+?)</Count>", search_data)[0])
        pmid = re.findall("<Id>(\d+?)</Id>", search_data)
        
        # efetch settings
        fetch_eutil = 'efetch.fcgi?'
        retmax = min(5, request.max_documents)  # Download in batches of 5 or less
        retstart = 0
        fetch_retmode = "&retmode=text"
        fetch_rettype = "&rettype=abstract"
        
        # Extract webenv and querykey
        fetch_webenv = "&WebEnv=" + re.findall("<WebEnv>(\S+)<\/WebEnv>", search_data)[0]
        fetch_querykey = "&query_key=" + re.findall("<QueryKey>(\d+?)</QueryKey>", search_data)[0]
        
        # Download abstracts
        run = True
        all_abstracts = []
        downloaded_files = []
        
        while run:
            fetch_retstart = "&retstart=" + str(retstart)
            fetch_retmax = "&retmax=" + str(retmax)
            fetch_url = base_url + fetch_eutil + db + fetch_querykey + fetch_webenv + fetch_retstart + fetch_retmax + fetch_retmode + fetch_rettype
            
            f = urllib.request.urlopen(fetch_url)
            fetch_data = f.read().decode('utf-8')
            abstracts = fetch_data.split("\n\n\n")
            all_abstracts.extend(abstracts)
            
            # Save abstracts to files
            for i, abstract in enumerate(abstracts):
                if retstart + i >= len(pmid) or len(downloaded_files) >= request.max_documents:
                    break
                    
                abs_fields = abstract.split("\n\n")
                if len(abs_fields) >= 5:  # Make sure we have enough fields
                    filename = f"{pmid[retstart + i]}.txt"
                    filepath = os.path.join(documents_dir, filename)
                    with open(filepath, "w", encoding='utf-8') as fp_text:
                        fp_text.write(abs_fields[4].replace("\n", ""))
                    downloaded_files.append(filepath)
            
            if len(downloaded_files) >= request.max_documents or retstart + retmax >= total_abstract_count:
                break
                
            # Wait to avoid API rate limits
            sleep(1)
            retstart += retmax
        
        # Embed the downloaded documents
        if downloaded_files:
            index = upload_documents(directory_path=documents_dir)
            if not index:
                return {"status": "partial_success", "message": "Documents downloaded but embedding failed", "downloaded": len(downloaded_files)}
        
        return {
            "status": "success",
            "message": f"Downloaded and embedded {len(downloaded_files)} abstracts",
            "query": request.query,
            "document_count": len(downloaded_files)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during PubMed search: {str(e)}")
