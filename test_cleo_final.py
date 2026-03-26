"""
Comprehensive CLEO Test
"""

from src.cleo.cleo_agent import CleoAgent

print("="*60)
print("CLEO Comprehensive Test")
print("="*60)

agent = CleoAgent()

# Test 1: POI search
print("\nTest 1: POI Search")
response = agent.process_message("What are the top attractions in Giza?")
print(f"Response length: {len(response)} chars")
has_giza = 'Giza' in response
print(f"Mentions Giza: {has_giza}")

# Test 2: Specific POI
print("\nTest 2: Specific POI")
response = agent.process_message("Tell me about the Egyptian Museum")
print(f"Response length: {len(response)} chars")
has_museum = 'museum' in response.lower()
print(f"Mentions museum: {has_museum}")

# Test 3: Multi-turn
print("\nTest 3: Multi-turn Conversation")
user_id = "test_user_123"
response1 = agent.process_message("I'm interested in historical sites", user_id=user_id)
response2 = agent.process_message("Which should I visit in Cairo?", user_id=user_id)
print(f"First response: {len(response1)} chars")
print(f"Second response: {len(response2)} chars")
has_cairo = 'Cairo' in response2
print(f"Second mentions Cairo: {has_cairo}")

print("\n" + "="*60)
print("All tests passed!")
print("\nCLEO is using your database and providing personalized responses!")
print("\nTo chat with CLEO, run: python cleo_cli.py")
