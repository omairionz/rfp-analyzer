# extract_tier3.py

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
import json
import re

TIER3_SYSTEM_CONTEXT = """
FILL HERE
"""

TIER3_PROMPT = """
FILL HERE
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

