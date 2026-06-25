# extract_tier1.py

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
import json
import re

TIER1_SYSTEM_CONTEXT = """
FILL HERE
"""

TIER1_PROMPT = """
FILL HERE
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
    








