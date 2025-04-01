#!/bin/bash

import re
import urllib.request
from time import sleep



def main():
    # user inputs what you want to search pubmed for
    query = input("Enter the query keywords such as 'cyanobacteria' to bulk download abstracts? Enter your keyword(s):")
    query2 = input("how many abstracts you need to download?")

    # if spaces were entered, replace them with %20 to make compatible with PubMed search
    query = query.replace(" ", "%20")

    # common settings between esearch and efetch
    base_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    db = 'db=pubmed'

    # esearch settings
    search_eutil = 'esearch.fcgi?'
    search_term = '&term=' + query
    search_usehistory = '&usehistory=y'
    search_rettype = '&rettype=json'

    # call the esearch command for the query and read the web result
    search_url = base_url + search_eutil + db + search_term + search_usehistory + search_rettype
    print("this is the esearch command:\n" + search_url + "\n")
    f = urllib.request.urlopen(search_url)
    search_data = f.read().decode('utf-8')

    # extract the total abstract count
    total_abstract_count = int(re.findall("<Count>(\d+?)</Count>", search_data)[0])

    # fetch pmid
    pmid = re.findall("<Id>(\d+?)</Id>", search_data)

    print("Type of pmid = ", type(pmid))
    print("Len of pmid = ", len(pmid))
    print("First abstract ID = ", int(pmid[0]))

    # efetch settings
    fetch_eutil = 'efetch.fcgi?'
    retmax = 5
    retstart = 0
    fetch_retmode = "&retmode=text"
    fetch_rettype = "&rettype=abstract"

    # obtain webenv and querykey settings from the esearch results
    fetch_webenv = "&WebEnv=" + re.findall("<WebEnv>(\S+)<\/WebEnv>", search_data)[0]
    fetch_querykey = "&query_key=" + re.findall("<QueryKey>(\d+?)</QueryKey>", search_data)[0]

    # call efetch commands using a loop until all abstracts are obtained
    run = True
    all_abstracts = list()
    loop_counter = 1

    while run:
        print("Efectch number " + str(loop_counter))
        loop_counter += 1
        fetch_retstart = "&retstart=" + str(retstart)
        fetch_retmax = "&retmax=" + str(retmax)
        # create the efetch url
        fetch_url = base_url + fetch_eutil + db + fetch_querykey + fetch_webenv + fetch_retstart + fetch_retmax + fetch_retmode + fetch_rettype
        print(fetch_url)
        # open the efetch url
        f = urllib.request.urlopen(fetch_url)
        fetch_data = f.read().decode('utf-8')
        # split the data into individual abstracts
        abstracts = fetch_data.split("\n\n\n")
        # append to the list all_abstracts
        all_abstracts = all_abstracts + abstracts
        print("a total of " + str(len(all_abstracts)) + " abstracts have been downloaded.\n")
        if len(all_abstracts) >= int(query2):
            break

        # wait 5 seconds so we don't get blocked
        sleep(5)
        # update retstart to download the next chunk of abstracts
        retstart = retstart + retmax
        if retstart > total_abstract_count:
            run = False

    print(all_abstracts)

    abstract_count = 0
    for abstract in all_abstracts:
        abs_fields = abstract.split("\n\n")
        print("Currently processing PMID = ", pmid[abstract_count])
        print("Length of ABSTRACT_FIELD = ", len(abs_fields))
        path_to_write_text = "./" + pmid[abstract_count] + ".txt"
        with open(path_to_write_text, "w", encoding='utf-8') as fp_text:
            fp_text.write(abs_fields[4].replace("\n", ""))

        abstract_count += 1


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

