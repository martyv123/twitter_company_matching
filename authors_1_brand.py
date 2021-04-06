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

AUTHOR_BRANDS = []
BRANDS = []

def load_brands():
    """
    Load brand information into a list of dictionaries in the global list `BRANDS`.
    Makes for easier lookups as opposed to constantly opening/searching through file.
    """
    global BRANDS
    with open('brand_twitter.csv', mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            ugov_id = row["ugov_id"]
            brand_name_tax = row["brand_name_tax"]
            twitter_handle_1 = row["TwitterHandle"].strip('@')
            twitter_handle_2 = row["TwitterHandle2"].strip('@')
            brand_dict = {"ugov_id": ugov_id, "brand_name_tax": brand_name_tax, "TwitterHandle": twitter_handle_1, "TwitterHandle2": twitter_handle_2}
            BRANDS.append(brand_dict)

def author_brand_match():
    """
    Match authors with their respective brands.
    Writes to a temporary file called `authors_1_brand_tmp.csv'.
    """
    global AUTHOR_BRANDS

    # Build list of brand twitter handles to do matches on
    brand_handles = []
    for brand in BRANDS:
        brand_handles.append(brand["TwitterHandle"])
        if brand["TwitterHandle2"]:
            brand_handles.append(brand["TwitterHandle2"])

    with open('authors_1_brand.csv', mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        count = 0
        for row in csv_reader:
            count += 1
            print("Author Brand Match: " + str(count))
            # fuzzywuzzy matching for best match
            author = row["Author"]
            match_tuple = process.extractOne(author, brand_handles)
            match = match_tuple[0]
            match_score = match_tuple[1]
            # Let's cap at a 60% match to avoid some bad matches
            if match_score >= 60:
                for brand in BRANDS:
                    if match == brand["TwitterHandle"]:
                        match_dict = {"Author": author, "ugov_id": brand["ugov_id"], "brand_name_tax": brand["brand_name_tax"],
                                        "match_score": match_score, "TwitterHandle": brand["TwitterHandle"], 
                                        "TwitterHandle2": brand["TwitterHandle2"]}
                        AUTHOR_BRANDS.append(match_dict)
                        break
                    elif match == brand["TwitterHandle2"]:
                        match_dict = {"Author": author, "ugov_id": brand["ugov_id"], "brand_name_tax": brand["brand_name_tax"],
                                        "match_score": match_score, "TwitterHandle": brand["TwitterHandle"], 
                                        "TwitterHandle2": brand["TwitterHandle2"]}
                        AUTHOR_BRANDS.append(match_dict)
                        break
            else:
                match_dict = {"Author": author, "ugov_id": '', "brand_name_tax": '', "match_score": '', 
                                "TwitterHandle": '', "TwitterHandle2": ''}
                AUTHOR_BRANDS.append(match_dict)

    # Write to tmp file authors_1_brand_tmp.csv
    with open('authors_1_brand_tmp.csv', mode='w', encoding='utf-8-sig', newline='') as csv_file:
        fieldnames = ["Author", "ugov_id", "brand_name_tax", "match_score", "TwitterHandle", "TwitterHandle2"]
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=',')
        csv_writer.writeheader()
        csv_writer.writerows(AUTHOR_BRANDS)
                

if __name__ == "__main__":
    print("Starting twitter_matching script...")
    print("Loading brands into dictionary...")
    load_brands()
    
    print("Matching authors with their respective brands...")
    author_brand_match()

    print("Matching script complete.")
    sys.exit(0)