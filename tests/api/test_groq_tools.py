"""
Test Groq Tool Call Format
Figure out the correct format for Groq API
"""

from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Test different tool formats
tools_v1 = [
    {
        "type": "function",
        "function": {
            "name": "search_pois",
            "description": "Search POIs",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        }
    }
]

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Search for POIs about Cairo"}
]

print("Test 1: With tools parameter")
try:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        tools=tools_v1
    )
    print(f"Response type: {type(response)}")
    print(f"Response: {response}")

    # Check different response structures
    if hasattr(response, 'choices'):
        print(f"Has choices: {len(response.choices)}")
        if response.choices:
            msg = response.choices[0].message
            print(f"Message type: {type(msg)}")
            print(f"Message: {msg}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60 + "\n")

print("Test 2: Without tools (should work)")
try:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    print(f"Success! Response: {response.choices[0].message.content[:100]}")
except Exception as e:
    print(f"Error: {e}")
