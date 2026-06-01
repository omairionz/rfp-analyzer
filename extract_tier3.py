# extract_tier3.py

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
import json
import re

TIER3_SYSTEM_CONTEXT = """
Return only JSON output - no markdown, no commentary.
You are the world's best senior Request for Proposal (RFP) analyst specializing in extracting evaluation criteria and award methodology..
Extract the data the fields request from the text below.
Focus on Section M specifically. Section M - Evaluation Factors for Award
Do not guess. If you are uncertain, set confidence to 'low'. 
If value is missing, include it in fields_missing and return null.
If value is inferred, include it in fields_inferred and reduce confidence.
"""

TIER3_PROMPT = """
Return a JSON object with exactly these fields:
- evaluation_criteria: (string or null)
- evaluation_factors: (list of strings or null)
- factor_relative_importance: (string or null)
- factor_weights: (string or null) - each should have a percentage with total adding to 100%
- past_performance_required: (string) - "Yes" or "No"
- past_performance_requirements: (string or null)
- past_performance_reference_count: (number or null)
- clearance_requirements: (list of strings or null)
- certifications_or_qualifications_required: (list of strings or null)
- oral_presentations_or_demonstrations: (string) "Yes", "No", or provided explanation
- model: "claude-sonnet-4-5"
- confidence: "high", "medium", "low"
- fields_inferred: (list of strings or null)
- fields_missing: (list of strings or null)
"""

# extraction call
def extract_tier3(text: str) -> dict:
    llm = ChatAnthropic(model="claude-sonnet-4-5", temperature=0)
    prompt = f"{TIER3_PROMPT}\n\nDocument Text:\n\n{text}"

    response = llm.invoke([
        SystemMessage(content=TIER3_SYSTEM_CONTEXT),
        HumanMessage(content=prompt)
    ])

    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', response.content, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise

