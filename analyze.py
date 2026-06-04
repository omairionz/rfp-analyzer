# analyze.py -> CLI output

from dotenv import load_dotenv
load_dotenv() # very first thing loaded in program

import json
import os
from src.extract_tier1 import extract_tier1
from src.extract_tier2 import extract_tier2
from src.extract_tier3 import extract_tier3
from src.parse_rfp import generate_database, get_first_pages_text, get_relevant_text, find_section_m_pages, tier3_page_content

# TODO: Don't fully understand this --> review
def save_output(extraction_result: dict, solicitation_number: str, tier: str):
    folder = os.path.join("outputs", solicitation_number) # names an output folder like this: output/1234567890
    os.makedirs(folder, exist_ok=True) # creates the folder and any parent folders needed using that name; if outputs folder exists, move on
    path = os.path.join(folder, f"{tier}.json") # creates and creates a path for .json files
    with open(path, "w") as f:  # loops through each path in write mode
        json.dump(extraction_result, f, indent=2) # converts Python Dictionary into .json format and puts it in file f
    print(f"Saved to {path}") # confirmation

def main():
    # allows load_documents to extract PDF text from ALL FOLDERS in data
    rfp_folders = os.listdir("data") # returns list of folders in data; ["RFP-1", "RFP-2", "RFP-3"]

    for rfp_folder in rfp_folders: # loops through one folder at a time
        print("Loading documents...")
        documents = generate_database(rfp_folder)

        print("Extracting text...")
        tier1_text = get_first_pages_text(documents)
        tier2_text = get_relevant_text(rfp_folder)

        print("Running extractions...")
        tier1_result = extract_tier1(tier1_text)
        tier2_result = extract_tier2(tier2_text)

        tier3_result = None
        page_numbers = find_section_m_pages(documents, rfp_folder)
        if not page_numbers:
            print("Unable to find Section M. Skipping Tier 3.")
        else:
            tier3_text = tier3_page_content(documents, page_numbers)
            tier3_result = extract_tier3(tier3_text)

        print("Saving output...")
        sol = tier1_result["solicitation_number"]
        save_output(tier1_result, sol, "tier1")
        save_output(tier2_result, sol, "tier2")
        if tier3_result:
            save_output(tier3_result, sol, "tier3")

if __name__ == "__main__":
    main()

