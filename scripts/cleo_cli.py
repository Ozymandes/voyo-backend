#!/usr/bin/env python3
"""
CLEO CLI - Interactive Testing Interface
Cairo Local Expert & Operator - Egyptian Travel Guide
"""

import argparse
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.cleo.cleo_agent import CleoAgent
from src.cleo.user_profile_manager import UserProfileManager

def print_header(profile=None):
    """Print CLEO welcome header"""
    print("\n" + "="*60)
    print("  CLEO - Your Egyptian Travel Guide")
    print("="*60)

    if profile:
        name = profile.get('full_name', 'friend')
        print(f"\nAhlan, {name}!")
    else:
        print("\nAhlan wa sahlan!")

    print("I'm CLEO, your knowledgeable Egyptian friend and guide.")
    print("Ask me about Egyptian attractions, history, culture, or travel tips!")
    print("\nCommands:")
    print("  'profile' - View your travel profile")
    print("  'debug' - Toggle debug mode")
    print("  'stats' - View conversation statistics")
    print("  'quit' or 'exit' - End conversation")
    print("-"*60 + "\n")

def print_profile(profile):
    """Display user profile"""
    print("\n" + "="*60)
    print("  Your Travel Profile")
    print("="*60)
    print(f"Name: {profile.get('full_name', 'N/A')}")
    print(f"Age Range: {profile.get('age_range', 'N/A')}")
    print(f"Itinerary Pace: {profile.get('itinerary_pace', 'N/A')}")
    print(f"Mobility: {profile.get('mobility_preference', 'N/A')}")
    print(f"Budget: {profile.get('trip_budget_estimate', 'N/A')} EGP/day")

    interests = profile.get('interest_scores', {})
    if interests:
        print(f"\nInterest Scores:")
        for category, score in interests.items():
            print(f"  - {category}: {score}/5")

    print("="*60 + "\n")

def print_stats(stats):
    """Display conversation statistics"""
    print("\n" + "="*60)
    print("  Conversation Statistics")
    print("="*60)
    print(f"Total Messages: {stats['total_messages']}")
    print(f"Your Messages: {stats['user_messages']}")
    print(f"CLEO Messages: {stats['assistant_messages']}")
    if stats['first_message']:
        print(f"First Message: {stats['first_message']}")
    if stats['last_message']:
        print(f"Last Message: {stats['last_message']}")
    print("="*60 + "\n")

def main():
    """Main CLI loop"""
    parser = argparse.ArgumentParser(description="CLEO - Egyptian Travel Guide")
    parser.add_argument("--debug", action="store_true", help="Show debug info")
    parser.add_argument("--user-id", default="test_user", help="User ID for testing")
    args = parser.parse_args()

    try:
        print("Initializing CLEO...")
        agent = CleoAgent()
        profile_manager = UserProfileManager()

        user_id = args.user_id
        profile = profile_manager.get_profile(user_id)

        print_header(profile)

        # Main chat loop
        while True:
            try:
                user_input = input("You: ").strip()

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nMa'a salama! Safe travels!\n")
                    break

                if user_input.lower() == 'profile':
                    if profile:
                        print_profile(profile)
                    else:
                        print("\nNo profile found. Create one with --new-profile\n")
                    continue

                if user_input.lower() == 'stats':
                    stats = agent.memory.get_conversation_stats(user_id)
                    print_stats(stats)
                    continue

                if user_input.lower() == 'debug':
                    args.debug = not args.debug
                    print(f"\nDebug mode: {'ON' if args.debug else 'OFF'}\n")
                    continue

                if not user_input:
                    continue

                # Process message
                print("\nCLEO thinking...")
                response = agent.process_message(
                    user_input,
                    user_id=user_id,
                    debug=args.debug
                )

                # Print response safely (remove emojis for Windows console)
                safe_response = response.encode('ascii', 'ignore').decode('ascii')
                print(f"\nCLEO: {safe_response}\n")

            except KeyboardInterrupt:
                print("\n\nMa'a salama! Safe travels!\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                if args.debug:
                    import traceback
                    traceback.print_exc()

    except Exception as e:
        print(f"\n❌ Failed to initialize CLEO: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
