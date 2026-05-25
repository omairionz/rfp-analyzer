# extract_tier1.py

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
import json
import re

TIER1_SYSTEM = """
You are extracting structured data from a federal government RFP.
Extract the fields below from the provided text. 
Return ONLY valid JSON — no commentary, no markdown fences.
If a field is not present, return null.
Do not guess. If you're uncertain, set confidence to "low".
"""

TIER1_PROMPT_SCHEMA = """
Return a JSON object with exactly these fields:
- solicitation_number (string or null)
- agency (string or null)
- sub_agency_office (string or null)
- title (string or null)
- naics_codes along with industry name (list of strings)
- psc_codes (list of strings)
- set_aside_type (string or null)
- contract_type (string or null)
- due_date (string in ISO 8601 format with timezone, or null)
- estimated_value_min (number or null)
- estimated_value_max (number or null)
- period_of_performance (string or null)
- place_of_performance (string or null)
- contracting_officer with subfields: name, email, phone (all string or null)
- confidence ("high", "medium", or "low")
- fields_inferred (list of field names you had to infer/guess rather than read directly)
"""

def extract_tier1(text: str) -> dict:
    llm = ChatAnthropic(model="claude-sonnet-4-5", temperature=0)
    prompt = f"{TIER1_PROMPT_SCHEMA}\n\nDocument Text:\n\n{text}"

    response = llm.invoke([
        SystemMessage(content=TIER1_SYSTEM),
        HumanMessage(content=prompt)
        ])
    
    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', response.content, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise
    








