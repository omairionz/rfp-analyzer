# extract_tier2.py

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
import json
import re

TIER2_SYSTEM_CONTEXT = """
Return only JSON output - no markdown, no commentary.
You are the world's best senior Request for Proposal (RFP) analyst at extracting submission requirements, proposal instructions, and formatting.
Extract the data the fields request from the text below.
Do not guess. If you are uncertain, set confidence to 'low'. 
If value is missing, include it in fields_missing and return null.
If value is inferred, include it in fields_inferred and reduce confidence.
"""

TIER2_PROMPT = """
Return a JSON object with exactly these fields:
- page_limit_total: (string or null)
- volume_structure: (list of strings or null)
- volume_page_limits: (list of strings or null)
- format_requirements: (all string or null) subfields: font, font_size, spacing, margins, file_format, naming_convention
- submission_method: (string or null)
- submission_email: (string or null)
- submission_deadline: (string with local time or null) "MM/DD/YYYY HH:MM TZ" format
- late_submission_policy: (string or null)
If explicitly stated, extract exact policy
If missing, include in fields_missing and return null.
- required_forms: (list of strings or null)
- required_certifications: (list of strings or null)
- amendment_acknowledgement_required: (string - "Yes" or "No")
- signature_required: (string - "Yes" or "No")
- number_of_copies with subfields - electronic: (number or null), hard_copy: (number or null)
- pre_proposal_conference with subfields - required: (string) "Yes" or "No", date: (string or null) format: MM/DD/YYYY, location: (string, "virtual", or null)
- qa_deadline: (string or null) "MM/DD/YYYY HH:MM TZ" format
- step_requirements: 
    step_1 (string or null)
    step_2 (string or null)
    step_3 (string or null)
- model: "claude-sonnet-4-5"
- confidence: "high", "medium", "low"
- fields_inferred: (list of strings or null)
- fields_missing: (list of strings or null) fields that are assigned null for any reason. If subfield, label as parent.child (e.g. step_requirements.step_3)
"""

def extract_tier2(text: str) -> dict:
    llm = ChatAnthropic(model="claude-sonnet-4-5", temperature=0)
    prompt = f"{TIER2_PROMPT}\n\nDocument Text:\n\n{text}"

    response = llm.invoke([
        SystemMessage(content=TIER2_SYSTEM_CONTEXT),
        HumanMessage(content=prompt)
        ])
    
    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', response.content, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise