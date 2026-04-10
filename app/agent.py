# app/agent.py

from app.llm import call_azure_openai
from app.tools import get_weather, calculator

TOOLS = {
    "get_weather": get_weather,
    "calculator": calculator
}


SYSTEM_PROMPT = """
You are an AI agent.

You can use tools when needed.

Available tools:
1. get_weather(city)
2. calculator(expression)

If a tool is needed, respond ONLY in this format:
TOOL_CALL: tool_name | argument

Otherwise, respond normally.
"""


async def run_agent(messages):

    # Step 1: Add system prompt
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    # Step 2: Ask LLM what to do
    response = await call_azure_openai(messages)

    # Step 3: Check if tool is requested
    if response.startswith("TOOL_CALL:"):
        try:
            _, tool_part = response.split("TOOL_CALL:")
            tool_name, arg = tool_part.strip().split("|")

            tool_name = tool_name.strip()
            arg = arg.strip()

            # Step 4: Execute tool
            tool_func = TOOLS.get(tool_name)

            if not tool_func:
                return "Unknown tool"

            tool_result = await tool_func(arg)

            # Step 5: Send tool result back to LLM
            messages.append({
                "role": "assistant",
                "content": response
            })

            messages.append({
                "role": "user",
                "content": f"Tool result: {tool_result}"
            })

            final_response = await call_azure_openai(messages)

            return final_response

        except Exception as e:
            return f"Tool execution error: {str(e)}"

    # Step 6: Normal response
    return response