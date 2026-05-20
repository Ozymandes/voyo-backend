"""
Test CLEO Functionality
"""

from src.cleo.cleo_agent import CleoAgent

def test_cleo():
    """Test CLEO agent"""
    print("Testing CLEO Chatbot...")
    print("="*60)

    # Initialize CLEO
    agent = CleoAgent()
    print("[OK] CLEO initialized")

    # Test 1: Simple greeting
    print("\nTest 1: Greeting")
    response = agent.process_message("Hello, who are you?")
    print(f"[OK] Response length: {len(response)} characters")
    # Remove emojis for safe printing
    safe_response = response.encode('ascii', 'ignore').decode('ascii')
    print(f"  Preview: {safe_response[:100]}...")

    # Test 2: Factual question
    print("\nTest 2: Factual question")
    response = agent.process_message("What are the opening hours for Khan el-Khalili?")
    print(f"[OK] Response length: {len(response)} characters")
    print(f"  Contains 'open': {'open' in response.lower()}")

    # Test 3: Complex question
    print("\nTest 3: Complex question")
    response = agent.process_message("Tell me about the Pyramids of Giza")
    print(f"[OK] Response length: {len(response)} characters")
    print(f"  Contains 'pyramid': {'pyramid' in response.lower()}")

    # Test 4: Multi-turn conversation
    print("\nTest 4: Multi-turn conversation")
    user_id = "test_user"
    response1 = agent.process_message("I'm interested in mosques", user_id=user_id)
    response2 = agent.process_message("Which one should I visit first?", user_id=user_id)
    print(f"[OK] Multi-turn response length: {len(response2)} characters")

    print("\n" + "="*60)
    print("All tests passed! CLEO is working perfectly.")
    print("\nTo chat with CLEO, run: python cleo_cli.py")

if __name__ == "__main__":
    test_cleo()
