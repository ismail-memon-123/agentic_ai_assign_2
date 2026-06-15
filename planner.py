import json
import re

from memory import (
    read_mem,
    write_mem
)

from mcp_tools import TOOLS

MAX_STEPS = 8

def parse_action(text):

    print("h1")
    print(text.strip())
    print("/h1")
    text = text.strip()

    think = re.match(
        r"^THINK\((.*)\)$",
        text,
        flags=re.S
    )

    if think:
        return (
            "THINK",
            None,
            None,
            think.group(1)
        )

    finish = re.match(
        r"^FINISH\((.*)\)$",
        text,
        flags=re.S
    )

    if finish:
        return (
            "FINISH",
            None,
            None,
            finish.group(1)
        )

    tool = re.match(
        r"^TOOL\(([^,]+),\s*(\{.*\})\)$",
        text,
        flags=re.S
    )

    if tool:

        return (
            "TOOL",
            tool.group(1).strip(),
            json.loads(tool.group(2)),
            None
        )

    return (
        "PARSE_ERROR",
        None,
        None,
        text
    )

def call_tool(name, args):

    if name not in TOOLS:
        raise Exception(
            f"Unknown tool: {name}"
        )

    return TOOLS[name](**args)

def plan_loop(llm_call, question, session_id="demo"):

    write_mem(
        session_id,
        "TASK",
        question
    )

    step = 0
    errors = 0

    while step < MAX_STEPS:
        print("increment")
        step += 1

        memory = read_mem(session_id)

        prompt = f"""
You are an autonomous ReAct agent.

Your job is to solve the user's task using reasoning, tools, observations, and memory.

AVAILABLE TOOLS

1. file_read_csv

Arguments:
{{
  "sample": integer
}}

Returns:
{{
  "columns": [...],
  "preview": [...]
}}

Use this tool whenever you need rows from the CSV dataset.

--------------------------------------------------

2. compute_stats

Arguments:
{{
  "rows": [...],
  "column": string
}}

Returns:
{{
  "count": number,
  "sum": number,
  "mean": number,
  "min": number,
  "max": number
}}

Use this tool to compute stats on a specific column of the rows data.

--------------------------------------------------

QUESTION

{question}

--------------------------------------------------

WORKING MEMORY

{memory[-5000:]}

--------------------------------------------------

IMPORTANT REASONING RULES

Take the memory and understand where you are in the workflow and what actions have already been done, the last step should be FINISH. Before that there must be a number of THINK and TOOL steps. The first step is always going to be THINK.

THINK is a thought, an idea of how to solve the problem and what to do next.

TOOL calls one of the specific tools.

A TOOL step must be preceded and succeeded by a THINK ep, as you need to reason about what inputs will be fed to the tool and what to do to make sense of the outputs.

The second last step (before FINISH) must also be a THINK step as the final answer must be properly composed and you mut think of whether the final result actually answers the question.

--------------------------------------------------

OUTPUT FORMAT

You MUST output EXACTLY ONE of the following:

THINK(<reasoning>)

TOOL(<tool_name>, <valid_json>)

FINISH(<answer>)

---------------------------------------------

Remember:

- Only one action per response.
- Using the rules you know see where you are in the workflow from the memory (if its empty its brand new and you start with THINK) and output one action, whichever one is most appropriate
- Never output multiple actions.
- Do not call the same tool repeatedly unless the observation requires it.
- Do not finish until you have sufficient evidence from tool observations.
"""

        output = llm_call(prompt)

        print("\nLLM:")
        print(output)

        kind, name, args, payload = parse_action(output)

        if kind == "THINK":

            write_mem(
                session_id,
                "THOUGHT",
                payload
            )

            continue

        if kind == "FINISH":

            write_mem(
                session_id,
                "FINISH",
                payload
            )
            print("labubu")

            return payload

        if kind == "TOOL":

            try:

                result = call_tool(
                    name,
                    args
                )

                write_mem(
                    session_id,
                    "TOOL",
                    f"{name} {json.dumps(args)}"
                )

                write_mem(
                    session_id,
                    "OBS",
                    json.dumps(result)[:3000]
                )

                continue

            except Exception as e:

                errors += 1

                write_mem(
                    session_id,
                    "ERROR",
                    str(e)
                )

                if errors >= 2:
                    break

                continue

        errors += 1

        write_mem(
            session_id,
            "ERROR",
            f"Bad output: {output}"
        )

        if errors >= 2:
            break

    return "Planner exceeded limits"