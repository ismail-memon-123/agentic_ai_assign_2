from crewai import LLM

llm = LLM(
    #model="bedrock/anthropic.claude-3-haiku-20240307-v1:0",
    #region_name="us-east-1"
    model="gemini/gemini-2.5-flash"
)


def bedrock_llm_call(prompt: str):

    response = llm.call(prompt)

    return response.strip()
