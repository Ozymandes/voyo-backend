"""
Test CLEO safeguards integration
"""

import sys
sys.path.insert(0, "c:\\Users\\yasee\\OneDrive\\Desktop\\VOYO_Backend\\voyo-backend")

from src.cleo.cleo_agent import CleoAgent

# Initialize agent
agent = CleoAgent()

# Test queries
test_queries = [
    ("In-scope", "What are the opening hours for the Pyramids?"),
    ("Out-of-scope - Math", "Can you help me solve this math problem: 2x + 3 = 7?"),
    ("Out-of-scope - Politics", "What's the current political situation in Egypt?"),
    ("Out-of-scope - France", "What's the capital of France?"),
    ("Out-of-scope - Cooking", "How do I bake a chocolate cake?")
]

print("Testing CLEO Safeguards Integration")
print("=" * 70)

for category, query in test_queries:
    print(f"\n[{category}] Query: {query}")
    try:
        response = agent.process_message(query, debug=False)
        print(f"Response: {response[:200]}...")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 70)
