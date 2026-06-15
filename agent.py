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