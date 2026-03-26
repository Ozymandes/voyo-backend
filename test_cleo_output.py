"""
CLEO Output Test - Saves results to file to avoid console encoding issues
"""

from src.cleo.cleo_agent import CleoAgent
import json

agent = CleoAgent()

# Test CLEO with various questions
test_queries = [
    "What are the top attractions in Giza?",
    "Tell me about historical mosques in Cairo",
    "What should I know about visiting the Egyptian Museum?",
    "I'm interested in Islamic architecture"
]

results = []

for query in test_queries:
    print(f"Testing: {query[:50]}...")
    response = agent.process_message(query)

    results.append({
        "query": query,
        "response": response,
        "length": len(response),
        "mentions_egypt": "Egypt" in response,
        "has_arabic": any(word in response for word in ["Ahlan", "salaam", "Shukran", "Yalla", "Inshallah"]),
        "has_historical": any(word in response.lower() for word in ["historical", "history", "ancient", "built"])
    })

# Save results to JSON file
with open("cleo_test_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 80)
print("RESULTS SAVED TO: cleo_test_results.json")
print("=" * 80)

# Print summary
print("\nSUMMARY:")
for i, result in enumerate(results, 1):
    print(f"\nTest {i}:")
    print(f"  Query: {result['query']}")
    print(f"  Response length: {result['length']} chars")
    print(f"  Mentions Egypt: {result['mentions_egypt']}")
    print(f"  Uses Arabic phrases: {result['has_arabic']}")
    print(f"  Has historical context: {result['has_historical']}")
    print(f"  Preview: {result['response'][:150]}...")
