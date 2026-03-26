"""
Quick test of CLEO
"""

from src.cleo.cleo_agent import CleoAgent

agent = CleoAgent()
response = agent.process_message("Hello! What can you tell me about Egypt?")
print("CLEO says:")
print(response.encode('ascii', 'ignore').decode('ascii'))
print("\nTest complete!")
