# analyze.py --> only runnable file

# very first thing loaded in program
from dotenv import load_dotenv
load_dotenv()

import json
import os
from src.extract_tier1 import extract_tier1
from src.extract_tier2 import extract_tier2
from src.parse_rfp import generate_database, get_first_pages_text, get_relevant_text

def save_output(result: dict, solicitation_number: str, tier: str):
    folder = os.path.join("outputs", solicitation_number)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{tier}.json")
    with open(path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Saved to {path}")

def main():
    rfp_folders = os.listdir("data")  # ["RFP-1", "RFP-2", "RFP-3"]

    for rfp_folder in rfp_folders:
        print("Loading documents...")
        documents = generate_database(rfp_folder)

        print("Extracting text...")
        tier1_text = get_first_pages_text(documents)
        tier2_text = get_relevant_text(rfp_folder)

        print("Running extractions...")
        tier1_result = extract_tier1(tier1_text)
        tier2_result = extract_tier2(tier2_text)

        print("Saving output...")
        save_output(tier1_result, tier1_result["solicitation_number"], "tier1")
        save_output(tier2_result, tier1_result["solicitation_number"], "tier2")



if __name__ == "__main__":
    main()

