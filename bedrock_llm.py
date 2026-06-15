from planner import plan_loop

from bedrock_llm import (
    bedrock_llm_call
)

question = """
What is the mean of order_total?
Use the CSV preview and compute_stats.
"""

answer = plan_loop(
    bedrock_llm_call,
    question,
    session_id="session1"
)

print("\nFINAL ANSWER")
print(answer)
[ec2-user@ip-172-31-35-181 mcp-server]$ cat bedrock_llm.py
from crewai import LLM

llm = LLM(
    #model="bedrock/anthropic.claude-3-haiku-20240307-v1:0",
    #region_name="us-east-1"
    model="gemini/gemini-2.5-flash"
)


def bedrock_llm_call(prompt: str):

    response = llm.call(prompt)

    return response.strip()