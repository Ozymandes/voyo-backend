"""
Test full tool call cycle with Groq
"""

from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Simulated tool cycle
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_pois",
            "description": "Search for POIs",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        }
    }
]

messages = [
    {"role": "system", "content": "You are CLEO, an Egyptian travel guide."},
    {"role": "user", "content": "What attractions are in Cairo?"}
]

print("STEP 1: Calling LLM with tools")
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=messages,
    tools=tools
)

message = response.choices[0].message
print(f"Message content: {message.content}")
print(f"Tool calls: {message.tool_calls}")

if message.tool_calls:
    print("\nSTEP 2: Processing tool calls")
    for tool_call in message.tool_calls:
        print(f"Tool: {tool_call.function.name}")
        print(f"Args: {tool_call.function.arguments}")

        # Simulate tool result
        tool_result = {
            "pois": [
                {"name": "Khan el-Khalili", "category": "Historical"},
                {"name": "Egyptian Museum", "category": "Cultural"}
            ]
        }

        print(f"Result: {tool_result}")

        # Add assistant message
        messages.append({
            "role": "assistant",
            "content": message.content
        })

        # Add tool response
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(tool_result)
        })

    print("\nSTEP 3: Calling LLM again with tool results")
    final_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )

    print(f"Final response: {final_response.choices[0].message.content[:200]}...")

print("\n" + "="*60)
print("Tool call cycle successful!")
