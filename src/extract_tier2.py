# extract_tier2.py

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
import json
import re

TIER2_SYSTEM = """
You are extracting data from a federal government RFP.
Extract the fields below from the provided text. 
Return ONLY valid JSON — no commentary, no markdown fences.
If a field is not present, return null.
Do not guess. If you're uncertain, set confidence to "low".
"""

TIER2_PROMPT_SCHEMA = """
Return a JSON object with exactly these fields:
- page_limit_total (string or null)
- volume_structure e.g. "Volume I: Technical, Volume II: Past Performance" (string or null)
- format_requirements with subfields: font, margins, file type (PDF? Word?) (string or null)
- submission_method (string or null)
- required_forms (list of strings, e.g. ["SF1449", "SF33"])
- number_of_copies required (string or null)
- pre_proposal_conference (string or null)
- qa_deadline (string or null)
- step_requirements (null if single-phase solicitation, otherwise object with subfields):
    - step_1 with subfields: due_date, requirements, evaluation_guidance (all string or null)
    - step_2 with subfields: due_date, requirements, evaluation_guidance (all string or null)
    - step_3 with subfields: due_date, requirements, evaluation_guidance (all string or null)
- confidence ("high", "medium", or "low")
- fields_inferred (list of field names)
"""

def extract_tier2(text: str) -> dict:
    llm = ChatAnthropic(model="claude-sonnet-4-5", temperature=0)
    prompt = f"{TIER2_PROMPT_SCHEMA}\n\nDocument Text:\n\n{text}"

    response = llm.invoke([
        SystemMessage(content=TIER2_SYSTEM),
        HumanMessage(content=prompt)
        ])
    
    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', response.content, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise