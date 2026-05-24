# analyze.py

from dotenv import load_dotenv
load_dotenv()

import json
import os
from src.extract_tier1 import extract_tier1
from src.parse_rfp import generate_database, get_first_pages_text

def save_output(result: dict, solicitation_number: str):
    folder = os.path.join("outputs", solicitation_number)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "tier1.json")
    with open(path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Saved to {path}")

def main():
    print("Loading documents...")
    documents = generate_database()

    print("Extracting text...")
    text = get_first_pages_text(documents)

    print("Running Tier 1 extraction...")
    result = extract_tier1(text)

    print(json.dumps(result, indent=2))

    save_output(result, result["solicitation_number"])


if __name__ == "__main__":
    main()

