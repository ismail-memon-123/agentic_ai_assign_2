# MCP ReAct Agent with CrewAI and AWS Bedrock

## Overview

This project implements a ReAct-style AI agent that:

* Uses a custom planner loop
* Maintains append-only working memory
* Calls tools hosted on an AWS MCP server
* Uses Amazon Bedrock for LLM reasoning
* Demonstrates multi-step reasoning using THINK → TOOL → OBSERVE → FINISH

---

# Architecture

```text
User
  |
  v
Planner Loop (ReAct)
  |
  +--> Working Memory (Markdown)
  |
  +--> CrewAI LLM Wrapper
  |         |
  |         +--> AWS Bedrock
  |
  +--> MCP Tools
            |
            +--> file_read_csv
            +--> compute_stats
```

---

# Project Structure

```text
project/
│
├── agent.py
├── planner.py
├── memory.py
├── bedrock_llm.py
├── mcp_tools.py
├── requirements.txt
│
├── memory/
│   └── session1.md
│
└── README.md
```

---

# Prerequisites

## AWS

* AWS Account
* EC2 Instance
* Bedrock Model Access Enabled
* IAM User or Role with Bedrock permissions

## Software

* Python 3.10+
* pip
* AWS CLI

---

# Step-by-Step Instructions

## 1. Clone or Copy the Project

```bash
git clone <repository>
cd project
```

## 2. Create a Virtual Environment

```bash
python3 -m venv crewenv
source crewenv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Example:

```text
crewai
boto3
requests
pandas
```

## 4. Configure AWS Credentials

```bash
aws configure
```

Verify:

```bash
aws sts get-caller-identity
```

## 5. Start the MCP Server

On the EC2 instance:

```bash
python server.py
```

Verify:

```bash
curl http://<EC2_PUBLIC_IP>:8080/mcp/tools
```

Expected:

```json
{
  "tools": [
    {
      "name": "file_read_csv"
    },
    {
      "name": "compute_stats"
    }
  ]
}
```

## 6. Configure Bedrock

Set environment variables:

```bash
export AWS_REGION=us-east-1
export BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
```

## 7. Run the Agent

```bash
python agent.py
```

---

# Sample Data

Example CSV:

```csv
OrderID,OrderDate,CustomerName,Product,Quantity,UnitPrice,TotalAmount,Status
ORD0001,2026-03-12,David Wilson,Monitor,2,47.27,94.54,Shipped
ORD0002,2026-05-20,Bob Johnson,Smartphone,2,1018.28,2036.56,Cancelled
ORD0003,2026-02-25,David Wilson,Tablet,1,54.40,54.40,Pending
ORD0004,2026-06-16,Grace Taylor,Monitor,9,306.27,2756.43,Cancelled
ORD0005,2026-01-02,Carol Davis,Printer,10,424.50,4245.00,Delivered
```

---

# Example ReAct Workflow

Question:

```text
What is the mean of TotalAmount?
```

Expected execution:

```text
THINK(I need order data before computing statistics.)

TOOL(file_read_csv, {"sample":20})

OBS({...})

THINK(I now have rows and can compute statistics.)

TOOL(compute_stats, {"rows":[...], "column":"TotalAmount"})

OBS({"mean":3680.03})

THINK(I now have sufficient information.)

FINISH(The mean TotalAmount is 3680.03.)
```

---

# Example Memory File

```text
[2026-06-13T21:00:00.000001] TASK What is the mean of TotalAmount?

[2026-06-13T21:00:01.000001] THOUGHT I need order data before computing statistics.

[2026-06-13T21:00:02.000001] TOOL file_read_csv {"sample":20}

[2026-06-13T21:00:03.000001] OBS {"preview":[...]}

[2026-06-13T21:00:04.000001] THOUGHT I now have rows and can compute statistics.

[2026-06-13T21:00:05.000001] TOOL compute_stats {"rows":[...],"column":"TotalAmount"}

[2026-06-13T21:00:06.000001] OBS {"mean":3680.03}

[2026-06-13T21:00:07.000001] THOUGHT I now have sufficient information.

[2026-06-13T21:00:08.000001] FINISH The mean TotalAmount is 3680.03.
```

---

# Evaluation Questions

1. What is the mean of TotalAmount?
2. What is the maximum TotalAmount?
3. What is the minimum TotalAmount?
4. How many orders are present in the CSV preview?
5. What is the average UnitPrice?
6. What is the total revenue represented by the CSV preview?
7. Which customer appears most frequently?
8. Which product appears most frequently?
9. What percentage of orders are Cancelled?
10. Which month contains the highest revenue?

---

# Expected Outputs

| Question            | Expected Output                              |
| ------------------- | -------------------------------------------- |
| Mean TotalAmount    | FINISH(The mean TotalAmount is 3680.03.)     |
| Maximum TotalAmount | FINISH(The maximum TotalAmount is 13293.20.) |
| Minimum TotalAmount | FINISH(The minimum TotalAmount is 54.40.)    |
| Average UnitPrice   | FINISH(The average UnitPrice is 622.47.)     |
| Total Revenue       | FINISH(The total revenue is 73600.57.)       |

---

# Troubleshooting Tips

## Connection Refused

Error:

```text
Connection refused
```

Check:

```bash
sudo ss -tulpn | grep 8080
```

Expected:

```text
LISTEN 0 128 0.0.0.0:8080
```

---

## Connection Timeout

Error:

```text
Connection timed out
```

Verify:

* EC2 security group allows TCP port 8080
* Server is running
* Public IP address is correct

---

## Bedrock Access Denied

Error:

```text
AccessDeniedException
```

Verify:

* Model access has been granted
* IAM permissions are configured correctly
* AWS region matches the model region

---

## Tool Repeats Forever

Example:

```text
TOOL(file_read_csv)
TOOL(file_read_csv)
TOOL(file_read_csv)
```

Possible Causes:

* Prompt does not explain tool workflow
* Observation is missing or truncated
* Agent does not understand next step

Fixes:

* Improve ReAct prompt
* Add explicit THINK → TOOL → THINK instructions
* Reduce sample size

---

## Agent Never Finishes

Verify planner contains:

```python
if kind == "FINISH":
    return payload
```

---

## Parse Errors

Enable debugging:

```python
print("RAW:", repr(output))
print("PARSED:", kind)
```

Ensure the model outputs exactly one action:

```text
THINK(...)
TOOL(...)
FINISH(...)
```

---

# Success Criteria

The project is considered successful when:

* MCP server is reachable
* Bedrock responds successfully
* Tool calls execute correctly
* Memory file is generated
* ReAct workflow is visible
* Agent reaches FINISH state
* Evaluation questions are answered correctly
* Tool usage and observations are recorded in memory

---

# Technologies Used

* Python
* CrewAI
* AWS Bedrock
* boto3
* Flask
* MCP (Model Context Protocol)
* Pandas
* Requests
* Markdown Memory Store
