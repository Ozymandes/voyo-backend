"""
Test exact Groq tool format
"""

from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Test the exact format
messages = [
    {
        "role": "system",
        "content": "You are CLEO, an Egyptian travel guide. Use the search_pois function when asked about attractions."
    },
    {
        "role": "user",
        "content": "What attractions are in Cairo?"
    }
]

# Define tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_pois",
            "description": "Search for Points of Interest in Egypt",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for POIs"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

print("Calling Groq with tools...")
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=messages,
    tools=tools
)

print(f"Finish reason: {response.choices[0].finish_reason}")
print(f"Content: {response.choices[0].message.content}")

if response.choices[0].message.tool_calls:
    print(f"\nTool calls found:")
    for tc in response.choices[0].message.tool_calls:
        print(f"  ID: {tc.id}")
        print(f"  Name: {tc.function.name}")
        print(f"  Args: {tc.function.arguments}")
        print(f"  Type: {tc.type}")
