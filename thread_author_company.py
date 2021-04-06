import sys
import csv
from fuzzywuzzy import process

# Dataset consists of Twitter conversations using the hashtag #goodfood
# We are attempting to match the thread authors and authors to their respective brands/companies

# Threadauthor (366k) - author of thread
# Author (1.3m) - responder to thread
# Company (453) - company with Twitter handle
# Brand (1016) - owned by company, may/may not have own Twitter handle

# Goal: match Threadauthors and authors to Companies and Brands

# Roadmap: load all relevant info into dict once, search for matches using fuzzywuzzy, write results into file

THREAD_AUTHOR_COMPANIES = []
COMPANIES = []

def load_companies():
    """
    Load company information into a list of dictionaries in the global list `COMPANIES`.
    Makes for easier lookups as opposed to constantly opening/searching through file.
    """
    global COMPANIES
    with open('company_twitter.csv', mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            cik = row["cik"]
            conm = row["conm"]
            twitter_handle_1 = row["TwitterHandle"].strip('@')
            twitter_handle_2 = row["TwitterHandle2"].strip('@')
            company_dict = {"cik": cik, "conm": conm, "TwitterHandle": twitter_handle_1, "TwitterHandle2": twitter_handle_2}
            COMPANIES.append(company_dict)

def thread_author_company_match():
    """
    Match thread authors with their respective companies.
    Writes to a temporary file called `thread_author_company_tmp.csv'.
    """
    global THREAD_AUTHOR_COMPANIES

    # Build list of company twitter handles to do matches on
    company_handles = []
    for company in COMPANIES:
        company_handles.append(company["TwitterHandle"])
        if company["TwitterHandle2"]:
            company_handles.append(company["TwitterHandle2"])

    with open('threadauthors_company.csv', mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        count = 0
        for row in csv_reader:
            count += 1
            print("Thread Author Company Match: " + str(count))
            # fuzzywuzzy matching for best match
            thread_author = row["ThreadAuthor"]
            match_tuple = process.extractOne(thread_author, company_handles)
            match = match_tuple[0]
            match_score = match_tuple[1]
            # Let's cap at a 60% match to avoid some bad matches
            if match_score >= 60:
                for company in COMPANIES:
                    if match == company["TwitterHandle"]:
                        match_dict = {"ThreadAuthor": thread_author, "cik": company["cik"], "conm": company["conm"],
                                        "match_score": match_score, "TwitterHandle": company["TwitterHandle"], 
                                        "TwitterHandle2": company["TwitterHandle2"]}
                        THREAD_AUTHOR_COMPANIES.append(match_dict)
                        break
                    elif match == company["TwitterHandle2"]:
                        match_dict = {"ThreadAuthor": thread_author, "cik": company["cik"], "conm": company["conm"],
                                        "match_score": match_score, "TwitterHandle": company["TwitterHandle"], 
                                        "TwitterHandle2": company["TwitterHandle2"]}
                        THREAD_AUTHOR_COMPANIES.append(match_dict)
                        break
            else:
                match_dict = {"ThreadAuthor": thread_author, "cik": '', "conm": '', "match_score": '', 
                                "TwitterHandle": '', "TwitterHandle2": ''}
                THREAD_AUTHOR_COMPANIES.append(match_dict)

    # Write to tmp file thread_author_company_tmp.csv
    with open('thread_authors_company_tmp.csv', mode='w', encoding='utf-8-sig', newline='') as csv_file:
        fieldnames = ["ThreadAuthor", "cik", "conm", "match_score", "TwitterHandle", "TwitterHandle2"]
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=',')
        csv_writer.writeheader()
        csv_writer.writerows(THREAD_AUTHOR_COMPANIES)
                

if __name__ == "__main__":
    print("Starting twitter_matching script...")
    print("Loading companies into dictionary...")
    load_companies()
    
    print("Matching thread authors with their respective companies...")
    thread_author_company_match()

    print("Matching script complete.")
    sys.exit(0)