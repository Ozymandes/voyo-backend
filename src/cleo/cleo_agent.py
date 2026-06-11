"""
CLEO Agent — Genuine ReAct Orchestrator
Cairo Local Expert & Operator — Your Egyptian Travel Guide

Architecture (3 layers):
  1. Gate Layer  — SafetyFilter, ScopeDetector, ResponseClassifier (unchanged)
  2. Agent Core — Single LLM call with real tools; genuine ReAct loop (≤5 iters)
  3. Post-Processing — ResponseValidator, [PLANNER] injection, Supabase memory save
"""

import json
import logging
import re
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional

from src.cleo.config import CleoConfig, GroqClient, LLMResponse, config
from src.cleo.semantic_cache import SemanticCache
from src.cleo.conversation_memory import ConversationMemory
from src.cleo.prompts import (
    CLEO_SYSTEM_PROMPT,
    RESPONSE_STYLE_INSTRUCTIONS,
    format_cleo_response,
)
from src.cleo.tools import SupabaseTool, WeatherTool, WebSearchTool
from src.cleo.tools.profile_update_tool import ProfileUpdateTool
from src.cleo.user_profile_manager import UserProfileManager
from src.cleo.safeguards import ScopeDetector, SafetyFilter, ResponseValidator

logger = logging.getLogger(__name__)


class CleoAgent:
    """CLEO — Cairo Local Expert & Operator.

    Async-first agent with real tool calling, persistent memory, and a
    genuine ReAct loop.
    """

    def __init__(self):
        logger.info("Initializing CLEO agent (v2 — real ReAct)...")

        # Configuration
        self.config = CleoConfig()

        # LLM Client (Async Groq)
        self.llm = GroqClient()

        # Semantic Cache (optional Redis)
        self.cache = SemanticCache()

        # Conversation Memory (Supabase-backed)
        self.memory = ConversationMemory(
            max_history=self.config.max_conversation_history
        )

        # Tools — each exposes both sync and async methods
        self.tools = {
            "supabase": SupabaseTool(),
            "weather": WeatherTool(),
            "web_search": WebSearchTool(),
            "profile_update": ProfileUpdateTool(),
        }

        # Profile manager for per-request personalization
        self.profile_manager = UserProfileManager()

        # Safeguards (unchanged from v1 — they work well)
        self.scope_detector = ScopeDetector()
        self.safety_filter = SafetyFilter()
        self.response_validator = ResponseValidator()

        logger.info("CLEO agent initialized successfully")

    # ==================================================================
    # Public API
    # ==================================================================

    async def process_message(
        self,
        user_message: str,
        user_id: Optional[str] = None,
        debug: bool = False,
    ) -> str:
        """Process a user message through the full CLEO pipeline (async).

        This is the primary entry point called by the FastAPI route.
        """
        if debug:
            print(f"\n{'=' * 60}")
            print(f"USER MESSAGE: {user_message}")
            print(f"USER ID: {user_id or 'None (anonymous)'}")
            print(f"{'=' * 60}\n")

        # ── GATE LAYER ──────────────────────────────────────────────

        # Safety check
        safety_decision = self.safety_filter.check_query_safety(user_message)
        if not safety_decision.safe:
            logger.warning(f"Query flagged by safety filter: {safety_decision.reasoning}")
            return (
                safety_decision.suggested_response
                or "I cannot assist with that request. I'm designed to help with Egyptian travel and tourism."
            )

        # Fetch conversation context (Supabase-backed, survives restarts)
        conversation_context = ""
        if user_id:
            conversation_context = self.memory.get_context(user_id, last_n=10)
            if debug and conversation_context:
                print("CONVERSATION CONTEXT:\n" + conversation_context + "\n")

        # Scope detection (with context so follow-ups resolve properly)
        scope_decision = self.scope_detector.check_scope(
            user_message, conversation_context=conversation_context
        )
        if not scope_decision.in_scope:
            logger.info(f"Query out-of-scope: {scope_decision.reasoning}")
            return (
                scope_decision.redirection
                or "I specialize in Egyptian travel and tourism. How can I help you plan your Egypt trip?"
            )

        # ── PROFILE & STYLE ────────────────────────────────────────

        user_profile = None
        profile_context = ""
        if user_id:
            user_profile = self.profile_manager.get_personalization_context(user_id)
            if user_profile:
                profile_context = self._format_profile_context(user_profile)

        response_style = self._classify_response_style(user_message)

        # ── PERSIST USER MESSAGE ────────────────────────────────────

        if user_id:
            await self.memory.add_message_async(user_id, "user", user_message)

        # ── SEMANTIC CACHE CHECK ────────────────────────────────────

        if self._is_cacheable(user_message, response_style):
            cached = self.cache.get(user_message)
            if cached:
                if debug:
                    print("CACHE HIT!")
                if user_id:
                    await self.memory.add_message_async(user_id, "assistant", cached)
                return cached

        # ── AGENT CORE — Real ReAct Loop ────────────────────────────

        response = await self._agent_loop(
            user_message=user_message,
            user_id=user_id,
            conversation_context=conversation_context,
            profile_context=profile_context,
            response_style=response_style,
            debug=debug,
        )

        # ── POST-PROCESSING ────────────────────────────────────────

        response = self._post_process(response, user_message)

        # Persist assistant response
        if user_id:
            await self.memory.add_message_async(user_id, "assistant", response)

            # Auto-summarize old messages to keep context window lean
            try:
                await self.memory.maybe_summarize_async(user_id)
            except Exception as e:
                logger.warning(f"Summarization failed for {user_id}: {e}")

        # Update cache if appropriate
        if self._is_cacheable(user_message, response_style):
            self.cache.set(user_message, response)

        return response

    async def process_message_stream(
        self,
        user_message: str,
        user_id: Optional[str] = None,
        debug: bool = False,
    ) -> AsyncGenerator[str, None]:
        """Stream response chunks via SSE.

        Falls back to a single non-streamed response if the LLM decides
        to use tools (tool calls don't stream cleanly).
        """
        # Run the full pipeline but stream the final LLM call
        # For simplicity: run the normal pipeline, then yield chunks of the response
        # True token-level streaming can be added later when the frontend supports it
        response = await self.process_message(user_message, user_id, debug)
        # Simulate streaming by yielding chunks
        chunk_size = 5
        for i in range(0, len(response), chunk_size):
            yield response[i : i + chunk_size]

    # ==================================================================
    # Agent Core — Genuine ReAct Loop
    # ==================================================================

    async def _agent_loop(
        self,
        user_message: str,
        user_id: Optional[str] = None,
        conversation_context: str = "",
        profile_context: str = "",
        response_style: str = "standard",
        debug: bool = False,
    ) -> str:
        """Genuine ReAct loop.

        1. Send messages + tool definitions to Groq.
        2. If the LLM returns ``tool_calls`` → execute them → append
           results → loop back.
        3. If the LLM returns plain text → that is the final response.

        Up to ``config.max_agent_iterations`` iterations (default 5).
        """
        # Build the initial message list
        messages = self._build_messages(
            user_message, conversation_context, profile_context, response_style
        )

        # Get tool definitions for the LLM
        tool_defs = self._get_tool_definitions()

        max_iters = self.config.max_agent_iterations

        for iteration in range(max_iters):
            if debug:
                print(f"\n--- AGENT ITERATION {iteration + 1}/{max_iters} ---")

            llm_response: LLMResponse = await self.llm.generate_async(
                messages, tools=tool_defs
            )

            if debug:
                has_tools = llm_response.has_tool_calls
                content_preview = (llm_response.content or "")[:100]
                print(f"  has_tool_calls: {has_tools}")
                print(f"  content: {content_preview}...")

            # ── LLM is done — return the text ───────────────────────
            if not llm_response.has_tool_calls:
                return llm_response.content or ""

            # ── LLM wants to call tools → execute them ──────────────
            # Append the assistant's tool-call message to history
            messages.append(llm_response.to_message())

            for tool_call in llm_response.tool_calls:
                tool_name = tool_call.function.name
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    tool_args = {}

                if debug:
                    print(f"  TOOL CALL: {tool_name}({json.dumps(tool_args)[:120]})")

                # Execute the tool
                result = await self._execute_tool(tool_name, tool_args, user_id=user_id)

                # Append tool result as a tool-role message
                result_str = json.dumps(result) if isinstance(result, (dict, list)) else str(result)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result_str,
                })

                if debug:
                    preview = result_str[:150]
                    print(f"  TOOL RESULT ({tool_name}): {preview}...")

            # Loop continues — send tool results back to the LLM

        # Safety valve — max iterations exhausted
        logger.warning(f"Agent loop hit max iterations ({max_iters}) for: {user_message[:50]}")
        return "I apologize, I'm having difficulty processing that request. Could you rephrase it?"

    # ==================================================================
    # Tool Execution
    # ==================================================================

    async def _execute_tool(
        self, tool_name: str, tool_args: Dict, user_id: Optional[str] = None
    ) -> Any:
        """Execute a single tool call and return the result.

        All tool methods are wrapped with ``asyncio.to_thread`` when they
        are synchronous I/O-bound calls (Supabase, HTTP).
        """
        import asyncio

        try:
            if tool_name == "search_pois":
                return await self.tools["supabase"].search_pois_async(
                    query=tool_args.get("query", ""),
                    region=tool_args.get("region"),
                    category=tool_args.get("category"),
                    limit=tool_args.get("limit", 10),
                )

            elif tool_name == "get_poi_details":
                return await asyncio.to_thread(
                    self.tools["supabase"].get_poi_details,
                    poi_id=tool_args.get("poi_id"),
                )

            elif tool_name == "get_historical_info":
                return await asyncio.to_thread(
                    self.tools["supabase"].get_historical_significance,
                    poi_id=tool_args.get("poi_id"),
                )

            elif tool_name == "get_weather":
                return await asyncio.to_thread(
                    self.tools["weather"].get_current_weather,
                    city=tool_args.get("city", "Cairo"),
                )

            elif tool_name == "search_web":
                return await asyncio.to_thread(
                    self.tools["web_search"].search,
                    query=tool_args.get("query", ""),
                    num_results=tool_args.get("num_results", 5),
                )

            elif tool_name == "update_user_preference":
                if not user_id:
                    return {"error": "No user_id — cannot update profile for anonymous user."}
                return await asyncio.to_thread(
                    self.tools["profile_update"].update_preference,
                    user_id=user_id,
                    field=tool_args.get("field"),
                    value=tool_args.get("value"),
                    acknowledgment=tool_args.get("acknowledgment", ""),
                )

            elif tool_name == "curate_itinerary":
                # Bridge to Phase 2B — returns structured data for the
                # frontend to send to /api/v1/itinerary/optimize
                return self._handle_curate_itinerary(tool_args, user_id=user_id)

            else:
                return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}': {e}")
            return {"error": str(e)}

    def _handle_curate_itinerary(self, args: Dict, user_id: Optional[str] = None) -> Dict:
        """Handle the ``curate_itinerary`` tool call.

        Returns a structured payload that the frontend can POST to
        ``/api/v1/itinerary/optimize``.  The actual optimization happens
        in Phase 2B.
        """
        poi_ids = args.get("poi_ids", [])
        trip_duration_days = args.get("trip_duration_days", 1)
        region = args.get("region")
        preferences = args.get("preferences")

        return {
            "action": "curate_itinerary",
            "poi_ids": poi_ids,
            "trip_duration_days": trip_duration_days,
            "region": region,
            "preferences": preferences,
            "user_id": user_id,
            "status": "ready_for_optimization",
            "optimize_endpoint": "/api/v1/itinerary/optimize",
            "message": (
                f"Curated {len(poi_ids)} POIs for a {trip_duration_days}-day trip"
                + (f" in {region}" if region else "")
                + ". Send this payload to the optimize endpoint for scheduling."
            ),
        }

    # ==================================================================
    # Post-Processing
    # ==================================================================

    def _post_process(self, response: str, query: str) -> str:
        """Validate, format, and inject [PLANNER] token."""
        # 1. Run the ResponseValidator (was dead code — now active)
        validation = self.response_validator.validate(query, response)
        if not validation.valid:
            logger.warning(
                f"Response validation issues: {validation.issues} "
                f"(confidence={validation.confidence:.2f})"
            )
        if validation.warnings:
            logger.info(f"Response validation warnings: {validation.warnings}")

        # 2. Format (trim, ensure punctuation)
        formatted = format_cleo_response(response)

        # 3. Inject [PLANNER] token for itinerary responses
        if "[PLANNER]" not in formatted:
            day_headers = re.findall(r"(?:^|\n)\s*[\*#]*\s*Day\s+(\d+)", formatted)
            if len(set(day_headers)) >= 2:
                formatted += "\n[PLANNER]"
                logger.debug("[PLANNER] appended — itinerary detected")

        return formatted

    # ==================================================================
    # Message Construction
    # ==================================================================

    def _build_messages(
        self,
        user_message: str,
        conversation_context: str,
        profile_context: str,
        response_style: str,
    ) -> List[Dict[str, Any]]:
        """Build the full message list for the LLM."""
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": CLEO_SYSTEM_PROMPT}
        ]

        if profile_context:
            messages.append({"role": "system", "content": profile_context})

        if conversation_context:
            messages.append({
                "role": "system",
                "content": f"CONVERSATION HISTORY:\n{conversation_context}",
            })

        # Response length instruction
        style_instruction = RESPONSE_STYLE_INSTRUCTIONS.get(response_style, RESPONSE_STYLE_INSTRUCTIONS["standard"])
        messages.append({"role": "system", "content": style_instruction})

        # User's actual message
        messages.append({"role": "user", "content": user_message})

        return messages

    # ==================================================================
    # Tool Definitions for LLM
    # ==================================================================

    @staticmethod
    def _get_tool_definitions() -> List[Dict]:
        """Return the tool schemas the LLM can invoke."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_pois",
                    "description": (
                        "Search the database of 200+ Egyptian Points of Interest. "
                        "Returns POIs with names, categories, descriptions, locations, "
                        "ticket prices, opening hours, and visit duration. "
                        "Use this to find attractions, restaurants, mosques, temples, "
                        "museums, markets, or any place in Egypt."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for POIs (e.g., 'pyramids', 'museum in Cairo', 'King Tut')",
                            },
                            "region": {
                                "type": "string",
                                "description": "Egyptian region to filter by (Cairo, Giza, Alexandria, Luxor, Aswan, Sinai, Hurghada, Marsa Alam)",
                            },
                            "category": {
                                "type": "string",
                                "description": "POI category filter (historical, cultural, religious, natural, entertainment)",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default 10)",
                            },
                        },
                        "required": ["query"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_poi_details",
                    "description": (
                        "Get full details for a specific POI by its ID — including "
                        "historical significance, opening hours, ticket price, "
                        "average visit duration, images, and accessibility info."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "poi_id": {
                                "type": "integer",
                                "description": "The numeric ID of the POI",
                            },
                        },
                        "required": ["poi_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_historical_info",
                    "description": (
                        "Get detailed historical significance and cultural context "
                        "for a specific POI. Use when the user asks about history, "
                        "significance, or cultural background."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "poi_id": {
                                "type": "integer",
                                "description": "The numeric ID of the POI",
                            },
                        },
                        "required": ["poi_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get current weather for an Egyptian city",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "City name (Cairo, Giza, Alexandria, Luxor, Aswan, Hurghada, etc.)",
                            },
                        },
                        "required": ["city"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "search_web",
                    "description": "Search the web for current events, news, or the latest information about Egypt travel",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Web search query",
                            },
                        },
                        "required": ["query"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "update_user_preference",
                    "description": (
                        "Call this ONLY when the user explicitly states a personal travel preference "
                        '(e.g., "I love historical sites", "I hate beaches", "I prefer a relaxed pace"). '
                        "Do NOT call for vague mentions or questions."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "field": {
                                "type": "string",
                                "description": "Which profile field to update.",
                                "enum": [
                                    "interest_scores",
                                    "itinerary_pace",
                                    "price_sensitivity",
                                    "mobility_preference",
                                    "typical_companions",
                                ],
                            },
                            "value": {
                                "description": "New value for the field.",
                            },
                            "acknowledgment": {
                                "type": "string",
                                "description": "A short warm sentence to include in your response confirming what you saved.",
                            },
                        },
                        "required": ["field", "value", "acknowledgment"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "curate_itinerary",
                    "description": (
                        "Curate a list of POI IDs for an itinerary based on the user's request. "
                        "Call this when the user wants a trip plan and you've already used search_pois "
                        "to find relevant attractions. Returns POI IDs that the optimization engine "
                        "(Phase 2B VROOM) will arrange into an optimal schedule. "
                        "CLEO curates (picks POIs), the optimizer arranges (orders them)."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "poi_ids": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "List of POI IDs to include in the itinerary",
                            },
                            "region": {
                                "type": "string",
                                "description": "Region the itinerary covers",
                            },
                            "trip_duration_days": {
                                "type": "integer",
                                "description": "Number of days for the trip",
                            },
                            "preferences": {
                                "type": "object",
                                "description": "User preferences to consider for curation",
                            },
                        },
                        "required": ["poi_ids", "trip_duration_days"],
                    },
                },
            },
        ]

    # ==================================================================
    # Helpers
    # ==================================================================

    @staticmethod
    def _classify_response_style(query: str) -> str:
        """Classify the response length/style needed for this query.

        Returns "concise", "standard", or "detailed".
        """
        q = query.lower().strip()

        # ── DETAILED: itinerary / planning queries ──
        detailed_patterns = [
            r"\b(plan|itinerary|schedule|design|create|build|make)\b.{0,40}\b(trip|tour|visit|days?|week|travel)\b",
            r"\b\d+[\s\-]days?\b",
            r"\b(week|fortnight|weeks)\b.{0,30}\b(egypt|cairo|luxor|aswan|sinai|nile)\b",
            r"\bhow (should i|do i|can i) plan\b",
            r"\b(comprehensive|complete|full|detailed)\b.{0,20}\b(guide|itinerary|plan|tour)\b",
            r"\bwalk me through\b",
            r"\bwhat (should|can) i (do|see|visit).{0,20}\b\d+\s*days?\b",
        ]
        for pattern in detailed_patterns:
            if re.search(pattern, q):
                return "detailed"

        cities = ["cairo", "luxor", "aswan", "alexandria", "giza", "hurghada", "sinai", "sharm"]
        planning_words = ["plan", "itinerary", "trip", "visit", "travel", "tour", "day", "week", "route"]
        if sum(c in q for c in cities) >= 2 and any(w in q for w in planning_words):
            return "detailed"

        if q.count("?") >= 2:
            return "detailed"

        # ── CONCISE ──
        concise_starters = re.compile(
            r"^(when|what time|how much|how many|where is|where are|"
            r"is it|is there|does it|do they|can i|how far|how long does it take|"
            r"what('s| is) the (price|cost|fee|ticket|address|phone|rating|opening|closing))"
        )
        concise_keywords = re.compile(
            r"\b(opening hours?|closing time|ticket price|entrance fee|"
            r"address|location|phone number|contact|directions|how to get)\b"
        )
        depth_signals = re.compile(
            r"\b(tell me about|describe|explain|history of|significance|"
            r"recommend|suggest|what (should|can) i|best way)\b"
        )

        word_count = len(q.split())
        is_greeting = re.match(
            r"^(hi|hello|hey|thanks|thank you|ok|okay|great|got it|sure|yalla)", q
        )

        if is_greeting:
            return "concise"
        if word_count <= 12 and (concise_starters.match(q) or concise_keywords.search(q)) and not depth_signals.search(q):
            return "concise"

        # ── STANDARD ──
        return "standard"

    @staticmethod
    def _is_cacheable(query: str, response_style: str) -> bool:
        """Determine if a query should be checked against / stored in cache.

        Planning/itinerary queries should NOT be cached (they're
        personalized).  Simple factual queries can be cached.
        """
        if response_style == "detailed":
            return False
        q = query.lower()
        cacheable_keywords = [
            "open", "hours", "price", "ticket", "cost", "fee",
            "where", "location", "address", "phone", "contact",
            "rating", "review",
        ]
        return any(kw in q for kw in cacheable_keywords)

    @staticmethod
    def _format_profile_context(profile: Dict) -> str:
        """Format user profile into a context block for the system prompt."""
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

    # ==================================================================
    # Legacy sync wrapper (backward compat for scripts / tests)
    # ==================================================================

    def process_message_sync(
        self,
        user_message: str,
        user_id: Optional[str] = None,
        debug: bool = False,
    ) -> str:
        """Synchronous wrapper around ``process_message`` for non-async callers."""
        import asyncio
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # Already inside an event loop — create a new one in a thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(
                    asyncio.run,
                    self.process_message(user_message, user_id, debug),
                )
                return future.result()
        else:
            return asyncio.run(self.process_message(user_message, user_id, debug))
