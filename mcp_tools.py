import requests
from crewai.tools import BaseTool

MCP_URL = "http://127.0.0.1:8080/mcp"

def file_read_csv(sample=100):

    response = requests.post(
        f"{MCP_URL}/tools/file_read_csv",
        json={
            "sample": sample
        },
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def compute_stats(rows, column):

    response = requests.post(
        f"{MCP_URL}/tools/compute_stats",
        json={
            "rows": rows,
            "column": column
        },
        timeout=30
    )

    response.raise_for_status()

    return response.json()


TOOLS = {
    "file_read_csv": file_read_csv,
    "compute_stats": compute_stats
}