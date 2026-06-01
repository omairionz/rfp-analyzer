# extract_tier1.py

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
import json
import re

TIER1_SYSTEM_CONTEXT = """
Return only JSON output - no markdown, no commentary.
You are the world's best senior Request for Proposal (RFP) analyst at extracting structured metadata & details.
Extract the data the fields request from the text below.
Do not guess. If you are uncertain, set confidence to 'low'. 
If value is missing, include it in fields_missing and return null.
If value is inferred, include it in fields_inferred and reduce confidence.
"""

TIER1_PROMPT = """
Return a JSON object with exactly these fields:
- solicitation_number: (string or null)
- agency: (string or null)
- sub_agency_offices: (list of strings or null)
- title: (string or null)
- naics_codes: (list of strings, codes only or null)
- psc_codes: (list of strings or null)
- set_aside_type: (string or null)
- notice_type: (string or null)
- procurement_type: (string or null)
- due_date: (string with local time or null) "MM/DD/YYYY HH:MM TZ" format
- estimated_value_min: (number or null)
- estimated_value_max: (number or null)
- period_of_performance: (string or null)
- place_of_performance: (string or null)
- contracting_officer: (all string or null), with subfields: name, email, phone. 
If name not found directly, attempt to get name from email, ONLY if pattern is first-name.middle-initial.last-name@domain.gov
(e.g. john.w.doe@army.mil to John W. Doe)
Otherwise set name to null. If pattern is ambiguous (e.g. cfejarang@usgs.gov), set name to null
- model: "claude-sonnet-4-5"
- confidence: "high", "medium", or "low" (string)
- fields_inferred: (list of strings or null)
- fields_missing: (list of strings or null) fields that are assigned null for any reason. If subfield, label as parent.sub (e.g. contracting_officer.name)
"""

def extract_tier1(text: str) -> dict: # returns in key-value pair format. name: "name", age: "age", etc.
    llm = ChatAnthropic(model="claude-sonnet-4-5", temperature=0)
    prompt = f"{TIER1_PROMPT}\n\nDocument Text:\n\n{text}"

    response = llm.invoke([
        SystemMessage(content=TIER1_SYSTEM_CONTEXT),
        HumanMessage(content=prompt)
        ])
    
    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', response.content, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise
    








