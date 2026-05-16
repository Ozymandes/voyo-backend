"""
CLEO Agent - Main REACT Orchestrator
Cairo Local Expert & Operator - Your Egyptian Travel Guide
"""

from typing import Dict, List, Optional
import json
import logging
from datetime import datetime

from src.cleo.config import CleoConfig, GroqClient
from src.cleo.semantic_cache import SemanticCache
from src.cleo.conversation_memory import ConversationMemory
from src.cleo.prompts import CLEO_SYSTEM_PROMPT, format_cleo_response
from src.cleo.tools import SupabaseTool, WeatherTool, WebSearchTool
from src.cleo.tools.profile_update_tool import ProfileUpdateTool
from src.cleo.user_profile_manager import UserProfileManager

logger = logging.getLogger(__name__)

class CleoAgent:
    """
    CLEO - Cairo Local Expert & Operator

    Your knowledgeable Egyptian travel guide with:
    - Multi-turn conversation context
    - Personalized recommendations
    - Historical and cultural expertise
    - Practical travel advice
    """

    def __init__(self):
        """Initialize CLEO agent"""
        logger.info("Initializing CLEO agent...")

        # Configuration
        self.config = CleoConfig()

        # LLM Client (Groq + Llama 3.1 70B)
        self.llm = GroqClient()

        # Semantic Cache
        self.cache = SemanticCache()

        # Conversation Memory
        self.memory = ConversationMemory(
            max_history=self.config.max_conversation_history
        )

        # Tools
        self.tools = {
            "supabase": SupabaseTool(),
            "weather": WeatherTool(),
            "web_search": WebSearchTool(),
            "profile_update": ProfileUpdateTool()
        }

        # Profile manager for per-request personalization
        self.profile_manager = UserProfileManager()

        logger.info("CLEO agent initialized successfully")

    def process_message(
        self,
        user_message: str,
        user_id: str = None,
        debug: bool = False
    ) -> str:
        """
        Process user message through REACT loop

        Args:
            user_message: User's input message
            user_id: Optional user ID for personalization
            debug: Show reasoning steps

        Returns:
            CLEO's response
        """
        if debug:
            print(f"\n{'='*60}")
            print(f"USER MESSAGE: {user_message}")
            print(f"USER ID: {user_id or 'None (anonymous)'}")
            print(f"{'='*60}\n")

        # Get conversation context
        conversation_context = ""
        if user_id:
            conversation_context = self.memory.get_context(user_id, last_n=10)
            if debug and conversation_context:
                print("CONVERSATION CONTEXT:")
                print(conversation_context)
                print()

        # Load user profile for personalization
        user_profile = None
        profile_context = ""
        if user_id:
            user_profile = self.profile_manager.get_personalization_context(user_id)
            if user_profile:
                profile_context = self._format_profile_context(user_profile)

        # REASON: Analyze query
        reasoning = self._reason(user_message, user_id, conversation_context)

        if debug:
            print("REASONING:")
            print(f"  Approach: {reasoning['approach']}")
            print(f"  Use Cache: {reasoning['use_cache']}")
            print(f"  Tools Needed: {reasoning.get('tools', [])}")
            print(f"  Complexity: {reasoning.get('complexity', 'unknown')}")
            print()

        # Add user message to memory
        if user_id:
            self.memory.add_message(user_id, "user", user_message)

        # Check semantic cache
        if reasoning["use_cache"]:
            cached = self.cache.get(user_message)
            if cached:
                if debug:
                    print("CACHE HIT! Returning cached response.")
                if user_id:
                    self.memory.add_message(user_id, "assistant", cached)
                return cached

        # ACT: Execute approach
        max_iterations = 5

        for iteration in range(max_iterations):
            if debug:
                print(f"ITERATION {iteration + 1}")

            if reasoning["approach"] == "direct_db":
                # Simple factual query - use database directly
                response = self._direct_database_query(
                    user_message,
                    reasoning
                )

                # Cache the response
                if reasoning["use_cache"]:
                    self.cache.set(user_message, response)

                # Add to memory
                if user_id:
                    self.memory.add_message(user_id, "assistant", response)

                return format_cleo_response(response)

            elif reasoning["approach"] == "llm_agent":
                # Complex query - use LLM with tools
                response = self._llm_agent_execution(
                    user_message,
                    conversation_context,
                    reasoning,
                    user_id=user_id,
                    user_profile=user_profile,
                    profile_context=profile_context,
                    debug=debug
                )

                # Cache if appropriate
                if reasoning["use_cache"]:
                    self.cache.set(user_message, response)

                # Add to memory
                if user_id:
                    self.memory.add_message(user_id, "assistant", response)

                return format_cleo_response(response)

        # Fallback
        logger.warning(f"Max iterations reached for: {user_message[:50]}...")
        return "I apologize, but I'm having trouble with that question. Could you rephrase it?"

    def _reason(self, query: str, user_id: Optional[str], context: str) -> Dict:
        """
        Analyze query and determine approach

        Args:
            query: User's query
            user_id: User ID (for profile lookup)
            context: Conversation context

        Returns:
            Reasoning dictionary
        """
        query_lower = query.lower()

        # Simple factual questions (cacheable)
        cacheable_patterns = [
            r"(when|open|hours)",
            r"(how much|price|ticket|cost|fee)",
            r"(where|location|address)",
            r"(phone|contact)",
            r"(rating|reviews?|stars?)"
        ]

        use_cache = any(
            pattern in query_lower
            for pattern in cacheable_patterns
        )

        # Simple factual → direct DB
        if use_cache and not any(word in query_lower for word in [
            "tell me about", "describe", "explain", "history",
            "significance", "culture", "recommend"
        ]):
            return {
                "approach": "direct_db",
                "use_cache": True,
                "tools": [],
                "complexity": "simple"
            }

        # Weather-dependent questions
        if "weather" in query_lower or "temperature" in query_lower:
            return {
                "approach": "llm_agent",
                "use_cache": False,  # Weather changes
                "tools": ["weather"],
                "complexity": "medium"
            }

        # Questions about attractions, POIs, locations → Use LLM with tools
        if any(word in query_lower for word in [
            "attraction", "poi", "place", "visit", "see", "temple", "mosque",
            "museum", "pyramid", "citadel", "market", "bazaar"
        ]):
            return {
                "approach": "llm_agent",
                "use_cache": False,
                "tools": ["supabase"],
                "complexity": "medium"
            }

        # Complex questions → LLM agent with tools
        return {
            "approach": "llm_agent",
            "use_cache": use_cache,
            "tools": ["supabase"],  # Enable tools for database queries
            "complexity": "medium"
        }

    def _direct_database_query(self, query: str, reasoning: Dict) -> str:
        """
        Handle simple factual queries directly from database

        Args:
            query: User's query
            reasoning: Reasoning dictionary

        Returns:
            Response text
        """
        try:
            # Extract POI name from query
            # Simple keyword matching (can be enhanced)
            words = query.lower().split()

            # Search for POI
            pois = self.tools["supabase"].search_pois(
                query=query,
                limit=1
            )

            if pois:
                poi = pois[0]

                # Build response based on query type
                if "hour" in query.lower() or "open" in query.lower():
                    hours = poi.get("opening_hours")
                    if hours:
                        if isinstance(hours, dict) and "weekday_text" in hours:
                            return f"{poi['name']} is open:\n" + \
                                   "\n".join(hours["weekday_text"][:5])
                        return f"Opening hours available for {poi['name']}."

                elif "price" in query.lower() or "cost" in query.lower() or "ticket" in query.lower():
                    price = poi.get("ticket_price")
                    if price:
                        return f"Ticket prices for {poi['name']}:\n" + \
                               f"- Tourists: {price} EGP\n" + \
                               f"- Egyptians: {price * 0.2:.0f} EGP"
                    else:
                        return f"{poi['name']} has free entry!"

                elif "where" in query.lower() or "location" in query.lower():
                    address = poi.get("address")
                    if address:
                        return f"{poi['name']} is located at: {address}"
                    return f"Location information available for {poi['name']}."

                else:
                    # General info
                    return f"{poi['name']} is a {poi.get('category', 'tourist attraction')} in Egypt."

            return "I couldn't find information about that place. Could you be more specific?"

        except Exception as e:
            logger.error(f"Error in direct DB query: {e}")
            return "I'm having trouble finding that information right now."

    def _llm_agent_execution(
        self,
        query: str,
        context: str,
        reasoning: Dict,
        user_id: Optional[str] = None,
        user_profile: Optional[Dict] = None,
        profile_context: str = "",
        debug: bool = False
    ) -> str:
        """
        Execute LLM agent with tools

        Args:
            query: User's query
            context: Conversation context
            reasoning: Reasoning dictionary
            debug: Show debug info

        Returns:
            Response text
        """
        try:
            # Build messages
            messages = [
                {"role": "system", "content": CLEO_SYSTEM_PROMPT}
            ]

            # Inject user profile for personalization
            if profile_context:
                messages.append({"role": "system", "content": profile_context})

            # Add conversation context
            if context:
                messages.append({
                    "role": "system",
                    "content": f"CONVERSATION HISTORY:\n{context}"
                })

            # Add user query
            messages.append({"role": "user", "content": query})

            # Get tool definitions
            tools = self._get_tool_definitions()

            if debug:
                print("SENDING TO LLM:")
                print(f"  Messages: {len(messages)}")
                print(f"  Tools: {len(tools)}")
                print()

            # Call LLM
            # Note: We're not using tools because Groq's LLM sometimes
            # generates tool calls in text format instead of structured format
            # Instead, we query database first, then pass results to LLM for formatting
            response = self.llm.generate(messages, tools=None)

            # If reasoning suggests using tools, do pre-query of database
            if reasoning.get("tools") and "supabase" in reasoning["tools"]:
                # Query database first to get POI data
                pois = self.tools["supabase"].search_pois(
                    query=query,
                    limit=5,
                    user_profile=user_profile
                )

                if pois:
                    # Add POI data to context
                    poi_info = f"\n\nRELEVANT ATTRACTIONS:\n"
                    for poi in pois[:3]:  # Top 3 POIs
                        poi_info += f"- {poi.get('name', '')} ({poi.get('category', '')})\n"

                    messages.append({
                        "role": "system",
                        "content": poi_info
                    })

                    # Call LLM again with database info
                    response = self.llm.generate(messages, tools=None)

            if debug:
                print("LLM RESPONSE TYPE:", type(response).__name__)

            # Handle tool calls
            if isinstance(response, dict) and "tool_calls" in response:
                if debug:
                    print("TOOL CALLS:", len(response["tool_calls"]))
                    for tc in response["tool_calls"]:
                        print(f"  Tool: {tc.function.name} with args: {tc.function.arguments}")

                # Execute tools
                tool_results = self._execute_tool_calls(response["tool_calls"], user_id=user_id)

                if debug:
                    print("TOOL RESULTS:", list(tool_results.keys()))
                    print()

                # Add assistant message (with tool calls)
                if response.get("content"):
                    messages.append({
                        "role": "assistant",
                        "content": response.get("content", "")
                    })

                # Add tool responses
                for tool_call in response["tool_calls"]:
                    tool_id = tool_call.id
                    tool_name = tool_call.function.name

                    # Get tool result
                    tool_result = tool_results.get(tool_name, {"error": "Tool not found"})

                    # Add tool response message (format as string, not JSON)
                    tool_result_str = json.dumps(tool_result) if isinstance(tool_result, (dict, list)) else str(tool_result)

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_id,
                        "name": tool_name,
                        "content": tool_result_str
                    })

                # Call LLM again with tool results
                if debug:
                    print("CALLING LLM AGAIN WITH TOOL RESULTS")

                final_response = self.llm.generate(messages)

                if isinstance(final_response, dict) and "content" in final_response:
                    return final_response["content"]

                return str(final_response)

            # Direct response (no tool calls)
            if isinstance(response, dict):
                return response.get("content", str(response))

            # String response (no tool calls)
            return response

        except Exception as e:
            logger.error(f"Error in LLM agent execution: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"

    def _format_profile_context(self, profile: Dict) -> str:
        """Format user profile into a context block injected into the system prompt."""
        lines = ["USER PROFILE (use this to personalize all responses):"]

        scores = profile.get("interest_scores", {})
        if scores:
            top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
            top_labels = [k.replace("_", " ") for k, v in top if v > 0.5]
            if top_labels:
                lines.append(f"- Top interests: {', '.join(top_labels)}")

        pace = profile.get("itinerary_pace")
        if pace:
            lines.append(f"- Travel pace: {pace.replace('_', ' ')}")

        sensitivity = profile.get("price_sensitivity", "")
        budget = profile.get("budget_estimate")
        if sensitivity:
            budget_str = f" (est. ${budget}/day)" if budget else ""
            lines.append(f"- Budget: {sensitivity}{budget_str}")

        mobility = profile.get("mobility_preference", "")
        if mobility and mobility != "Full mobility":
            lines.append(f"- Mobility: {mobility}")

        companions = profile.get("typical_companions", {})
        if companions and isinstance(companions, dict) and companions.get("type"):
            lines.append(f"- Travels: {companions['type']}")

        return "\n".join(lines)

    def _get_tool_definitions(self) -> List[Dict]:
        """
        Get tool definitions for LLM

        Returns:
            List of tool definitions
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_pois",
                    "description": "Search for Points of Interest in Egypt. Returns list of POIs with names, descriptions, categories, and details.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for POIs (e.g., 'mosques in Cairo', 'historical sites')"
                            },
                            "region": {
                                "type": "string",
                                "description": "Egyptian region (Cairo, Giza, Alexandria, Luxor, Aswan, Sinai, Hurghada, Marsa Alam)"
                            },
                            "category": {
                                "type": "string",
                                "description": "POI category (Historical, Cultural, Religious, Natural, Entertainment, etc.)"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_historical_info",
                    "description": "Get detailed historical significance and cultural context for a specific POI",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "poi_id": {
                                "type": "string",
                                "description": "POI ID (integer as string)"
                            }
                        },
                        "required": ["poi_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get current weather information for an Egyptian city",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "City name (Cairo, Giza, Alexandria, Luxor, Aswan, etc.)"
                            }
                        },
                        "required": ["city"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_user_preference",
                    "description": (
                        "Call this ONLY when the user explicitly and clearly states a personal travel preference "
                        "(e.g., 'I love historical sites', 'I hate beaches', 'I prefer a relaxed pace', "
                        "'I'm on a tight budget'). Do NOT call for vague mentions or questions. "
                        "After calling, include the acknowledgment string naturally in your response."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "field": {
                                "type": "string",
                                "description": "Which profile field to update.",
                                "enum": ["interest_scores", "itinerary_pace", "price_sensitivity",
                                         "mobility_preference", "typical_companions"]
                            },
                            "value": {
                                "description": (
                                    "New value. For interest_scores: dict like {'historical_sites': 0.9}. "
                                    "For itinerary_pace: 'packed_schedule'|'balanced'|'slow_flexible'. "
                                    "For price_sensitivity: 'budget'|'moderate'|'luxury'. "
                                    "For mobility_preference: 'Full mobility'|'Limited walking'|'Wheelchair accessible only'. "
                                    "For typical_companions: {'type': 'solo'|'couple'|'family'|'group'}."
                                )
                            },
                            "acknowledgment": {
                                "type": "string",
                                "description": (
                                    "A short, warm, natural sentence to include in your response confirming "
                                    "what you've saved. E.g.: 'I've noted that you love historical sites — "
                                    "I'll make sure your recommendations lean that way!'"
                                )
                            }
                        },
                        "required": ["field", "value", "acknowledgment"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_web",
                    "description": "Search web for current events, news, or latest information about Egypt",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

    def _execute_tool_calls(self, tool_calls, user_id: Optional[str] = None) -> Dict:
        """
        Execute tool calls from LLM

        Args:
            tool_calls: List of tool calls from LLM

        Returns:
            Dictionary of tool results
        """
        results = {}

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            try:
                if function_name == "search_pois":
                    results[function_name] = self.tools["supabase"].search_pois(
                        query=function_args.get("query", ""),
                        region=function_args.get("region"),
                        category=function_args.get("category"),
                        limit=10
                    )

                elif function_name == "get_historical_info":
                    results[function_name] = self.tools["supabase"].get_historical_significance(
                        poi_id=function_args.get("poi_id", "")
                    )

                elif function_name == "get_weather":
                    results[function_name] = self.tools["weather"].get_current_weather(
                        city=function_args.get("city", "Cairo")
                    )

                elif function_name == "search_web":
                    results[function_name] = self.tools["web_search"].search(
                        query=function_args.get("query", ""),
                        num_results=5
                    )

                elif function_name == "update_user_preference":
                    if not user_id:
                        results[function_name] = {"error": "No user_id — cannot update profile for anonymous user."}
                    else:
                        results[function_name] = self.tools["profile_update"].update_preference(
                            user_id=user_id,
                            field=function_args.get("field"),
                            value=function_args.get("value"),
                            acknowledgment=function_args.get("acknowledgment", "")
                        )

                else:
                    results[function_name] = {"error": f"Unknown tool: {function_name}"}

            except Exception as e:
                logger.error(f"Error executing {function_name}: {e}")
                results[function_name] = {"error": str(e)}

        return results
