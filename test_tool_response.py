"""
Test Groq tool response format
"""

from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

messages = [
    {
        "role": "system",
        "content": "You are CLEO. Use search_pois function."
    },
    {
        "role": "user",
        "content": "What attractions are in Cairo?"
    }
]

tools = [
    {
        "type": "function",
        "function": {
            "name": "search_pois",
            "description": "Search POIs",
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

# First call
print("STEP 1: Initial call")
response1 = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=messages,
    tools=tools
)

tool_call = response1.choices[0].message.tool_calls[0]
print(f"Tool call: {tool_call.function.name} with args: {tool_call.function.arguments}")

# Add assistant message (even if content is None)
messages.append({
    "role": "assistant",
    "content": response1.choices[0].message.content or ""
})

# Add tool response
tool_result = {"pois": [{"name": "Khan el-Khalili", "category": "Historical"}]}
messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,
    "name": tool_call.function.name,
    "content": json.dumps(tool_result)
})

print(f"\nSTEP 2: Calling with tool result")
print(f"Messages: {len(messages)}")

# Second call
try:
    response2 = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    print(f"Success! Response: {response2.choices[0].message.content[:200]}...")
except Exception as e:
    print(f"Error: {e}")
    print(f"Error type: {type(e)}")
