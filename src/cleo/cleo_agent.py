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
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.cleo.config import (
    CleoConfig,
    GroqClient,
    get_llm_client,
    LLMResponse,
    config,
    CLEO_FALLBACK_MESSAGE,
)
from src.cleo.semantic_cache import SemanticCache
from src.cleo.conversation_memory import ConversationMemory
from src.cleo.prompts import (
    CLEO_SYSTEM_PROMPT,
    RESPONSE_STYLE_INSTRUCTIONS,
    build_system_prompt,
    format_cleo_response,
)
from src.cleo.tools import SupabaseTool, WeatherTool, WebSearchTool, WikimediaImageTool
from src.cleo.tools.profile_update_tool import ProfileUpdateTool
from src.cleo.user_profile_manager import UserProfileManager
from src.cleo.safeguards import ScopeDetector, SafetyFilter, ResponseValidator

logger = logging.getLogger(__name__)


# ── Result envelope for tool-grounded responses ───────────────────────────
# Source pills (Tier 2 #3): every grounded answer carries the tools/sources
# it was built from so the UI can show honest provenance. ``confidence`` is a
# coarse heuristic (DB-grounded = high, web-only = medium, no tools = low)
# derived from which tools fired — never a number the model invents.

@dataclass
class SourceRef:
    """A single provenance entry shown as a source pill."""
    label: str               # e.g. "Karnak Temple", "OpenWeather (Luxor)"
    kind: str                # "database" | "weather" | "web" | "image"


@dataclass
class CleoResult:
    """Enriched response envelope returned by process_message / explain_poi."""
    text: str
    sources: List[SourceRef] = field(default_factory=list)
    confidence: str = "medium"   # "high" | "medium" | "low"
    # Every tool name dispatched through _execute_tool this turn, in call
    # order. Surfaces real routing to the client so QA can tell e.g.
    # search_pois (DB-grounded) from search_web (Tavily) from no-tools
    # (parametric/LLM-only). Not a provenance list — see ``sources``.
    tools_used: List[str] = field(default_factory=list)


# Map tool-name → (kind, fallback label) for source provenance.
_TOOL_SOURCE_KIND = {
    "search_pois": ("database", "VOYO verified database"),
    "get_poi_details": ("database", "VOYO verified database"),
    "get_historical_info": ("database", "VOYO verified database"),
    "get_weather": ("weather", "OpenWeather"),
    "search_web": ("web", "Web search"),
    "search_wikimedia_image": ("image", "Wikimedia Commons"),
}


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
        self.llm = get_llm_client()

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
            "wikimedia_image": WikimediaImageTool(),
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
            return CleoResult(
                text=(
                    safety_decision.suggested_response
                    or "I cannot assist with that request. I'm designed to help with Egyptian travel and tourism."
                ),
                sources=[],
                confidence="low",
            )

        # ── P4 fix: booking-intent hard pre-check ─────────────────────
        # VOYO is informational + planning, NOT a booking platform.
        # This fires BEFORE the scope_detector so that conversation
        # context (which can boost borderline queries to in-scope) cannot
        # re-admit a clear transactional booking intent. Catches the
        # observed regression: "Book me a 5-star hotel" after a Cairo
        # itinerary conversation passed scope and spun search_pois 5x.
        import re as _re_booking
        _booking_verb = r"\b(book|booking|reserve|reservation|buy|buying|purchase|purchasing|checkout|pay\s+for)\b"
        _booking_obj = r"\b(hotel|motel|room|suite|flight|airfare|airline|airbnb|villa|cabin|cruise\s+booking|tour\s+package|plane\s+ticket)\b"
        if (
            _re_booking.search(_booking_verb, user_message, _re_booking.I)
            and _re_booking.search(_booking_obj, user_message, _re_booking.I)
        ):
            logger.info(f"[SCOPE] booking-intent pre-check redirect for: {user_message[:60]}")
            return CleoResult(
                text=(
                    "I can't book hotels, flights, or tickets directly — VOYO is "
                    "a planning companion, not a booking platform. But I can "
                    "help you choose the best area to stay based on your "
                    "itinerary and budget, suggest what to look for, and plan "
                    "your days so you book the right nights. Where are you "
                    "thinking of staying?"
                ),
                sources=[],
                confidence="low",
            )

        # Fetch conversation context (Supabase-backed, survives restarts)
        conversation_context = ""
        if user_id:
            conversation_context = self.memory.get_context(user_id, last_n=4)
            if debug and conversation_context:
                print("CONVERSATION CONTEXT:\n" + conversation_context + "\n")

        # Scope detection (with context so follow-ups resolve properly)
        scope_decision = self.scope_detector.check_scope(
            user_message, conversation_context=conversation_context
        )
        if not scope_decision.in_scope:
            logger.info(f"Query out-of-scope: {scope_decision.reasoning}")
            # Booking-specific redirect: VOYO is informational/planning, not
            # a booking platform. A specific redirect reads as intentional
            # scope-safety, not a broken "rephrase it" fallback.
            import re as _re
            if _re.search(r"\b(book|booking|reserve|reservation|buy|purchase)\b", user_message, _re.I):
                booking_redirect = (
                    "I can't book hotels, flights, or tickets directly — VOYO is "
                    "a planning companion, not a booking platform. But I can "
                    "help you choose the best area to stay based on your "
                    "itinerary and budget, suggest what to look for, and plan "
                    "your days so you book the right nights. Where are you "
                    "thinking of staying?"
                )
                return CleoResult(
                    text=booking_redirect,
                    sources=[],
                    confidence="low",
                )
            return CleoResult(
                text=(
                    scope_decision.redirection
                    or "I specialize in Egyptian travel and tourism. How can I help you plan your Egypt trip?"
                ),
                sources=[],
                confidence="low",
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
                return CleoResult(text=cached, sources=[], confidence="medium")

        # ── AGENT CORE — Real ReAct Loop ────────────────────────────

        # Snapshot tool names for the [LLM] instrumentation line. The agent
        # loop logs the full request envelope (endpoint, model, tools made
        # available) so QA can verify routing from backend logs alone.
        _tool_names_available = [
            d.get("function", {}).get("name", "?")
            for d in self._get_tool_definitions()
        ]
        # request_id: short, unique per call, never contains secrets. Used to
        # correlate [LLM] / [TAVILY] / TOOL CALL log lines for one request.
        import uuid as _uuid
        _req_id = _uuid.uuid4().hex[:12]
        _model_name = getattr(self.llm, "model", "unknown")
        logger.info(
            "[LLM] request_id=%s endpoint=chat provider=%s model=%s "
            "streaming=false tools_available=%s",
            _req_id,
            type(self.llm).__name__,
            _model_name,
            _tool_names_available,
        )

        response, sources, tools_used = await self._agent_loop(
            user_message=user_message,
            user_id=user_id,
            conversation_context=conversation_context,
            profile_context=profile_context,
            response_style=response_style,
            debug=debug,
        )
        logger.info(
            "[LLM] request_id=%s status=complete tools_called=%s "
            "sources_count=%d",
            _req_id,
            tools_used,
            len(sources),
        )

        # ── POST-PROCESSING ────────────────────────────────────────

        response = self._post_process(response, user_message)

        # Confidence heuristic: DB-grounded → high, web-only → medium,
        # no tools fired → low (chitchat/general knowledge).
        kinds = {s.kind for s in sources}
        if "database" in kinds:
            confidence = "high"
        elif kinds:
            confidence = "medium"
        else:
            confidence = "low"

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

        return CleoResult(
            text=response,
            sources=sources,
            confidence=confidence,
            tools_used=tools_used,
        )

    # ==================================================================
    # POI_EXPLAIN — grounded deep-dive on a single POI
    # ==================================================================

    async def explain_poi(
        self,
        poi_id: int,
        user_message: Optional[str] = None,
        user_id: Optional[str] = None,
        debug: bool = False,
    ) -> CleoResult:
        """Explain a single POI in depth (the ``poi_explain`` intent).

        Loads the full POI row from Supabase, injects it as ground-truth
        system context, and instructs CLEO to write 2–3 grounded
        paragraphs, embed images inline, and end with a 3-question
        follow-ups JSON block.

        No gate layer — this is a structured request about a verified POI
        whose content is authoritative database data.
        """
        import asyncio

        # 1. Load the full POI row (ground truth)
        poi = await asyncio.to_thread(self.tools["supabase"].get_poi_details, poi_id)
        if not poi:
            logger.warning(f"explain_poi: POI id={poi_id} not found")
            return CleoResult(
                text=(
                    f"I couldn't find details for that place (POI id {poi_id}). "
                    "It may have been removed — try another attraction."
                ),
                sources=[],
                confidence="low",
            )

        name = poi.get("name", "this place")
        user_message = (user_message or "").strip() or f"Tell me about {name}."

        if debug:
            print(f"\n{'=' * 60}\nPOI_EXPLAIN — id={poi_id} name={name}\n{'=' * 60}")

        # 2. Build the ground-truth + formatting instruction
        poi_context = self._build_poi_explain_context(poi)

        # 3. Persist the user turn (best-effort)
        if user_id:
            try:
                await self.memory.add_message_async(user_id, "user", user_message)
            except Exception as e:
                logger.warning(f"explain_poi: failed to persist user message: {e}")

        # 4. Run the agent loop with POI ground truth + the wikimedia tool
        response, loop_sources, _tools_used = await self._agent_loop(
            user_message=user_message,
            user_id=user_id,
            conversation_context="",
            profile_context="",
            response_style="standard",
            debug=debug,
            extra_system_context=poi_context,
            include_wikimedia_image=True,
        )

        # 5. Sanitize — strip LLM tool-call artifacts (Groq/Llama sometimes
        #    leaks ``</function>`` tokens) and guarantee the message ends with
        #    exactly one clean, valid follow-ups JSON fence.
        response = self._sanitize_poi_explain_response(
            response if isinstance(response, str) else str(response)
        )

        # 6. Persist the assistant turn (best-effort)
        if user_id:
            try:
                await self.memory.add_message_async(user_id, "assistant", response)
            except Exception as e:
                logger.warning(f"explain_poi: failed to persist assistant message: {e}")

        # Source provenance: the POI's own DB record is always the primary
        # source (ground truth injected above); merge in any tool-sourced
        # refs (e.g. a Wikimedia image) collected by the loop.
        sources = [SourceRef(label=name, kind="database")] + [
            s for s in loop_sources if not (s.kind == "database" and s.label == name)
        ]
        return CleoResult(text=response, sources=sources, confidence="high")

    def _sanitize_poi_explain_response(self, response: str) -> str:
        """Repair common LLM artifacts in the POI_EXPLAIN output.

        Groq/Llama occasionally leaks tool-call tokens (``</function>``)
        into the content and can fumble the closing code fence. This
        guarantees:
          1. no stray ``<function>`` tags remain,
          2. the message ends with exactly one clean, valid
             ``json {"follow_ups": [...]}`` `` fence.
        """
        if not response:
            return response

        # 1. Strip leaked tool-call tags (Groq/Llama artifact)
        text = re.sub(r"</?function[^>]*>", "", response)

        # 2. Find the LAST fenced JSON block (the follow-ups must be final)
        blocks = list(re.finditer(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S))
        raw_json = blocks[-1].group(1) if blocks else None

        follow_ups = None
        if raw_json:
            try:
                parsed = json.loads(raw_json)
                if isinstance(parsed, dict) and isinstance(parsed.get("follow_ups"), list):
                    follow_ups = parsed["follow_ups"]
            except json.JSONDecodeError:
                follow_ups = None

        # 3. Cut everything from the start of that final block onward
        if blocks:
            text = text[: blocks[-1].start()].rstrip()
        elif raw_json is not None:
            text = text[: text.find(raw_json)].rstrip()

        text = text.rstrip()

        # 4. Re-append a single clean, validated follow-ups block (max 3)
        if follow_ups:
            clean = {"follow_ups": [str(q).strip() for q in follow_ups][:3]}
            text += "\n\n```json\n" + json.dumps(clean, ensure_ascii=False) + "\n```"
        else:
            # Could not parse — keep the cleaned narrative; do not fabricate.
            logger.warning("explain_poi: could not parse follow_ups JSON from response")

        return text

    def _build_poi_explain_context(self, poi: Dict) -> str:
        """Build the ground-truth record + formatting rules for POI_EXPLAIN."""
        name = poi.get("name", "this place")
        image_urls = poi.get("image_urls") or []
        has_images = bool(image_urls)

        ground_truth = {
            "name": name,
            "name_arabic": poi.get("name_arabic"),
            "category": poi.get("category"),
            "description": poi.get("description"),
            "historical_significance": poi.get("historical_significance"),
            "ticket_price": poi.get("ticket_price"),
            "currency": poi.get("currency", "EGP"),
            "opening_hours": poi.get("opening_hours"),
            "best_visit_times": poi.get("best_visit_times"),
            "average_visit_duration": poi.get("average_visit_duration"),
            "image_urls": image_urls,
        }

        lines = [
            f"## POI EXPLAIN MODE — explain **{name}** to the traveler.",
            "",
            "### AUTHORITATIVE DATABASE RECORD (your ONLY source of truth)",
            "```json",
            json.dumps(ground_truth, ensure_ascii=False, indent=2, default=str),
            "```",
            "",
            "### STRICT OUTPUT RULES (these override all other style instructions)",
            "1. **ANTI-HALLUCINATION CONTRACT (critical):** The JSON record above is your "
            "COMPLETE and ONLY source of truth. You are STRICTLY FORBIDDEN from using your "
            "own training knowledge — no construction dates, dimensions, weights, cardinal "
            "alignment, dynasty numbers, builder names (beyond what the `name` field itself "
            "states), or historical anecdotes unless they are LITERALLY written in the JSON "
            "fields above. Even if you 'know' famous facts about this place, you MUST OMIT "
            "them when they are absent from the record. The database is intentionally minimal "
            "for some POIs — a short, HONEST answer is far better than a detailed invented "
            "one. Before writing each sentence, verify every claim is backed by an explicit "
            "JSON value; if it is not, delete that sentence.",
            "   Then write 2–3 vivid paragraphs in CLEO's warm voice using ONLY these fields: "
            "description, historical_significance, ticket_price, opening_hours, "
            "best_visit_times, average_visit_duration. If most are empty/null, write less "
            "rather than invent — lean on the practical fields (price, hours, duration, best "
            "times) that ARE present.",
            "2. **Images:** Embed images inline as markdown: `![alt text](url)`.",
        ]
        if has_images:
            lines.append(
                f"   The record provides {len(image_urls)} image URL(s) in `image_urls`. "
                "Embed the best 1–2 inline where they fit naturally. Do not use any other URLs."
            )
        else:
            lines.append(
                "   ⚠️ `image_urls` is EMPTY in the database. You MUST call the "
                "`search_wikimedia_image` tool with the POI name to obtain a real image URL, "
                "then embed the returned URL. Do NOT output any image URL you did not get "
                "from that tool or from the database record."
            )
        lines += [
            "3. **Follow-ups:** End your ENTIRE message with exactly ONE fenced code block "
            "containing a JSON object with exactly 3 follow-up questions relevant to this POI:",
            "```json",
            '{"follow_ups": ["question 1?", "question 2?", "question 3?"]}',
            "```",
            "   Put this JSON block at the very end. Write the narrative + images first, "
            "then the single follow-ups block. Nothing should come after the closing fence.",
        ]
        return "\n".join(lines)

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
        extra_system_context: str = "",
        include_wikimedia_image: bool = False,
    ) -> tuple:
        """Genuine ReAct loop.

        1. Send messages + tool definitions to Groq.
        2. If the LLM returns ``tool_calls`` → execute them → append
           results → loop back.
        3. If the LLM returns plain text → that is the final response.

        Up to ``config.max_agent_iterations`` iterations (default 5).

        ``extra_system_context`` is appended as a final system message
        (highest priority) — used by POI_EXPLAIN to inject ground truth.
        ``include_wikimedia_image`` exposes the image-search tool.
        """
        # Build the initial message list
        messages = self._build_messages(
            user_message,
            conversation_context,
            profile_context,
            response_style,
            extra_system_context=extra_system_context,
        )

        # Get tool definitions for the LLM
        tool_defs = self._get_tool_definitions(
            include_wikimedia_image=include_wikimedia_image
        )

        max_iters = self.config.max_agent_iterations

        # Collected (tool_name, tool_args, result) tuples for source
        # provenance (Tier 2 #3 source pills).
        tool_invocations: List[tuple] = []

        # Determine whether to FORCE a tool call on the FIRST iteration.
        # Prevents the model from answering POI/itinerary queries purely
        # from training memory (hallucinating places/prices). Greetings are
        # classified "concise" so they are never trapped.
        #   - detailed (itineraries) → force search_pois (guaranteed DB grounding)
        #   - standard (POI descriptions, advice) → force SOME tool
        #   - concise / follow-up iterations → auto (model decides)
        first_iter_force: Any = None
        if response_style == "detailed":
            first_iter_force = "search_pois"
        elif response_style == "standard":
            first_iter_force = True

        # Recommendation intent override: queries asking for suggestions /
        # discoveries ("hidden gems", "best places", "recommend", "what to
        # see") MUST ground in the POI database — never parametric memory.
        # Without this, gpt-4o-mini non-deterministically answers "hidden
        # gems in Cairo" from training data (plausible but unverified POI
        # names, no region filter, no ticket/hours data). Forcing
        # search_pois specifically guarantees the region filter + real
        # records flow through, which is also what makes the Wadi-Wishwashi
        # region fix actually take effect.
        if self._is_recommendation_intent(user_message):
            first_iter_force = "search_pois"

        for iteration in range(max_iters):
            if debug:
                print(f"\n--- AGENT ITERATION {iteration + 1}/{max_iters} ---")

            llm_response: LLMResponse = await self.llm.generate_async(
                messages,
                tools=tool_defs,
                force_tool=first_iter_force if iteration == 0 else None,
            )

            if debug:
                has_tools = llm_response.has_tool_calls
                content_preview = (llm_response.content or "")[:100]
                print(f"  has_tool_calls: {has_tools}")
                print(f"  content: {content_preview}...")

            # ── LLM is done — return the text ───────────────────────
            if not llm_response.has_tool_calls:
                content = llm_response.content
                # Hardened empty-content path: the model sometimes returns an
                # empty/None string (truncated to nothing, content-filtered, or a
                # near-quota 200 with no body). Returning "" here used to make
                # CLEO go completely silent in the app. Substitute the shared
                # fallback message instead so the user always sees something.
                if not content or not content.strip():
                    logger.warning(
                        "CLEO: model returned empty content (finish_reason=%s); "
                        "substituting fallback message.",
                        llm_response.finish_reason,
                    )
                    return (
                        CLEO_FALLBACK_MESSAGE,
                        self._sources_from_invocations(tool_invocations),
                        [t[0] for t in tool_invocations],
                    )
                return (
                    content,
                    self._sources_from_invocations(tool_invocations),
                    [t[0] for t in tool_invocations],
                )

            # ── LLM wants to call tools → execute them ──────────────
            # Append the assistant's tool-call message to history
            messages.append(llm_response.to_message())

            # ── P5 fix: discovery-intent override for search_pois ────────
            # When the user asks for "hidden gems" / "lesser known" / etc,
            # the LLM often strips the discovery phrasing and calls
            # search_pois(query="Cairo") — which then hits Tier 2 (description
            # ilike) and returns the most famous POIs (Pyramids/Sphinx) by
            # text-match frequency. Detect the discovery intent from the
            # ORIGINAL user message and rewrite the query so the tool's
            # Tier 4 discovery-inverted ranking path fires.
            _user_lc = user_message.lower()
            _is_discovery = any(p in _user_lc for p in (
                "hidden gem", "lesser known", "lesser-known",
                "off the beaten", "off-beaten", "underrated",
                "secret spot", "secret places", "overlooked",
                "not touristy", "non-touristy", "local favorite",
            ))

            for tool_call in llm_response.tool_calls:
                tool_name = tool_call.function.name
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    tool_args = {}

                # Apply the discovery override to search_pois calls when the
                # user asked for hidden gems but the LLM passed a generic query.
                if (
                    tool_name == "search_pois"
                    and _is_discovery
                    and tool_args.get("region")
                    and tool_args.get("query", "").strip().lower()
                        in ("", tool_args["region"].strip().lower())
                ):
                    tool_args["query"] = "hidden gems"
                    if debug:
                        print(f"  [P5] discovery override: query → 'hidden gems'")

                if debug:
                    print(f"  TOOL CALL: {tool_name}({json.dumps(tool_args)[:120]})")

                # Execute the tool
                result = await self._execute_tool(tool_name, tool_args, user_id=user_id)

                # Record the invocation for source provenance (Tier 2 #3).
                tool_invocations.append((tool_name, tool_args, result))

                # Append tool result as a tool-role message
                result_str = json.dumps(result) if isinstance(result, (dict, list)) else str(result)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result_str,
                })

                # ── P2 fix: curate_itinerary is terminal ────────────────
                # The tool returns a "ready_for_optimization" payload that
                # the frontend consumes via the [PLANNER] token. The LLM
                # cannot actually POST to the optimize endpoint from inside
                # the chat loop, so leaving it to "finish the job" causes
                # it to re-call curate_itinerary until max_iter (observed:
                # 3 repeats then "rephrase it" fallback). When the tool
                # returns a ready payload, synthesize the final user-facing
                # response with the [PLANNER] token and break the loop.
                if (
                    tool_name == "curate_itinerary"
                    and isinstance(result, dict)
                    and result.get("status") == "ready_for_optimization"
                ):
                    poi_ids = result.get("poi_ids") or []
                    region = result.get("region") or "Egypt"
                    days = result.get("trip_duration_days") or 1
                    # Look up POI names so the frontend's natural-language
                    # itinerary parser (_parseItineraryStops) can extract
                    # real stops. Without named stops the import sheet is
                    # empty and tapping "Open Planner" just switches tabs
                    # without saving anything. (Demo regression fix.)
                    poi_names = self._lookup_poi_names(poi_ids)
                    synth = self._build_planner_synth(
                        poi_names=poi_names,
                        days=days,
                        region=region,
                    )
                    logger.info(
                        f"[PLANNER] curate_itinerary terminal: "
                        f"poi_count={len(poi_ids)} days={days} region={region} "
                        f"named={len(poi_names)}"
                    )
                    return (
                        synth,
                        self._sources_from_invocations(tool_invocations),
                        [t[0] for t in tool_invocations],
                    )

                if debug:
                    preview = result_str[:150]
                    print(f"  TOOL RESULT ({tool_name}): {preview}...")

            # Loop continues — send tool results back to the LLM

        # Safety valve — max iterations exhausted
        logger.warning(f"Agent loop hit max iterations ({max_iters}) for: {user_message[:50]}")
        return (
            "I apologize, I'm having difficulty processing that request. Could you rephrase it?",
            self._sources_from_invocations(tool_invocations),
            [t[0] for t in tool_invocations],
        )

    # ==================================================================
    # Tool Execution
    # ==================================================================

    def _sources_from_invocations(
        self, invocations: List[tuple]
    ) -> List[SourceRef]:
        """Build deduped source refs from the tools that fired in the loop.

        Database lookups surface the actual POI names (when extractable) so
        the pill reads e.g. "Karnak Temple" rather than a generic label.
        Falls back to the tool's generic label when names can't be parsed.
        """
        refs: List[SourceRef] = []
        seen: set = set()
        for tool_name, tool_args, result in invocations:
            kind, fallback = _TOOL_SOURCE_KIND.get(tool_name, (None, None))
            if kind is None:
                continue  # e.g. update_user_preference — not a citation source
            labels = self._extract_source_labels(tool_name, tool_args, result, fallback)
            for label in labels:
                key = (kind, label)
                if key in seen:
                    continue
                seen.add(key)
                refs.append(SourceRef(label=label, kind=kind))
        return refs

    @staticmethod
    def _extract_source_labels(
        tool_name: str, tool_args: Dict, result: Any, fallback: str
    ) -> List[str]:
        """Best-effort extraction of human labels from a tool result."""
        # Database tools: surface POI names from the returned rows.
        if tool_name in ("search_pois", "get_poi_details", "get_historical_info"):
            names: List[str] = []
            rows = result if isinstance(result, list) else [result]
            for row in rows:
                if isinstance(row, dict):
                    name = row.get("name")
                    if isinstance(name, str) and name.strip():
                        names.append(name.strip())
            # For get_historical_info the row is significance text, not a
            # named POI — fall back to the generic DB label in that case.
            return names if names else ([fallback] if tool_name != "get_historical_info" else [fallback])
        # Weather: surface the city the forecast was for.
        if tool_name == "get_weather":
            city = tool_args.get("city")
            return [f"OpenWeather ({city})" if city else fallback]
        return [fallback]

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
                    limit=min(tool_args.get("limit", 5), 5),
                )

            elif tool_name == "get_poi_details":
                # The model sometimes passes a POI NAME (e.g. "Karnak Temple")
                # instead of its integer ID. Resolve names → IDs via a quick
                # search so the tool still returns data instead of None.
                poi_id = tool_args.get("poi_id")
                resolved_id = await self._resolve_poi_id(poi_id)
                return await asyncio.to_thread(
                    self.tools["supabase"].get_poi_details,
                    poi_id=resolved_id,
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

            elif tool_name == "search_wikimedia_image":
                return await self.tools["wikimedia_image"].search_image_async(
                    query=tool_args.get("query", ""),
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

    async def _resolve_poi_id(self, poi_id: Any) -> Any:
        """Normalize a ``poi_id`` argument to an integer DB id.

        The LLM occasionally passes a POI *name* (e.g. ``"Karnak Temple"``)
        instead of the integer id that ``get_poi_details`` expects. When the
        value is not already an int, do a quick ``search_pois`` lookup and
        return the best match's id. Falls back to the original value (which
        will yield None downstream) if nothing is found.
        """
        # Already an int (or an int-like string) → use as-is.
        if isinstance(poi_id, int):
            return poi_id
        if isinstance(poi_id, str):
            stripped = poi_id.strip()
            if stripped.isdigit():
                return int(stripped)
            # Looks like a name → resolve via search.
            try:
                hits = await self.tools["supabase"].search_pois_async(
                    query=stripped, limit=1
                )
                if hits:
                    first_id = hits[0].get("id")
                    if first_id is not None:
                        return int(first_id)
            except Exception as e:
                logger.warning(f"Could not resolve POI name '{stripped}': {e}")
        return poi_id

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

    def _lookup_poi_names(self, poi_ids: list) -> List[Dict[str, Any]]:
        """Fetch minimal POI info (id, name, city) for the curated IDs.

        Used to build a [PLANNER] synth that the frontend's natural-language
        itinerary parser can extract real stops from. Returns rows ordered
        by ID for deterministic layout. Empty list on any failure — the
        synth still emits a valid (if thinner) message.
        """
        if not poi_ids:
            return []
        unique_ids = list(dict.fromkeys(int(p) for p in poi_ids if p is not None))
        try:
            from src.cleo.tools.supabase_tool import SupabaseTool
            tool = SupabaseTool()
            rows = (
                tool.db.admin_client.table("pois")
                .select("id, name, city")
                .in_("id", unique_ids)
                .execute()
            )
            data = rows.data or []
            # Preserve input order (LLM picked the order).
            by_id = {r["id"]: r for r in data}
            return [by_id[i] for i in unique_ids if i in by_id]
        except Exception as e:
            logger.warning(f"[PLANNER] POI name lookup failed: {e}")
            return []

    def _build_planner_synth(
        self, poi_names: List[Dict[str, Any]], days: int, region: str
    ) -> str:
        """Build the [PLANNER] user-facing reply.

        Layout is intentionally line-based with 'Day N' headers so the
        Flutter _parseItineraryStops regex (\\bDay (\\d+)\\b + POI-name
        lines) can extract real stops. Without named stops the import
        sheet is empty and tapping 'Open Planner' silently no-ops.

        Stop names are emitted WITHOUT a '(city)' suffix because the
        Flutter import path fuzzy-matches stop names against the DB via
        Supabase ilike — appending '(Cairo)' breaks the match and the
        stop falls through to a custom_title insert, which can then
        fail downstream. The day header already carries the region.
        """
        header = (
            f"[PLANNER] I've curated {len(poi_names)} stops for your "
            f"{days}-day trip in {region}. Here's the plan — tap "
            f"**Open Planner** below to lock in day-by-day scheduling "
            f"with real admission prices, opening hours, and travel times.\n"
        )
        if not poi_names:
            return header + "\n(Open the planner to finish building your trip.)"
        # Distribute stops across the requested days. We no longer
        # collapse to fewer days — the user explicitly asked for N days,
        # so respect that even if the LLM under-curated (2+1 for 3 POIs
        # over 2 days is acceptable; the prompt separately pushes the
        # LLM to curate ≥2/day). The previous collapse-when-sparse logic
        # turned a 2-day request into a 1-day trip, which surprised the
        # user. (Demo feedback.)
        per_day = max(1, (len(poi_names) + days - 1) // days)
        lines = [header]
        for d in range(days):
            chunk = poi_names[d * per_day : (d + 1) * per_day]
            if not chunk:
                break
            lines.append(f"\nDay {d + 1} — {region}")
            for stop in chunk:
                name = stop.get("name") or "Stop"
                lines.append(f"• {name}")
        return "\n".join(lines)

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
        # Two paths produce [PLANNER]: (a) the curate_itinerary terminal
        # synth in _agent_loop (preferred — has structured named stops),
        # and (b) this fallback, which fires when the LLM writes its own
        # multi-day itinerary in chat without calling curate_itinerary.
        # For path (b) we still inject the token AND append the same CTA
        # copy so the UX is consistent and the user knows to tap the
        # button. (Demo consistency fix — was: bare token, no CTA, so the
        # 'Open Planner' button appeared under a message that never told
        # the user to tap it.)
        if "[PLANNER]" not in formatted:
            day_headers = re.findall(r"(?:^|\n)\s*[\*#]*\s*Day\s+(\d+)", formatted)
            if len(set(day_headers)) >= 2:
                formatted += (
                    "\n\n**Tap Open Planner below** to lock in the full "
                    "day-by-day itinerary with real admission prices, opening "
                    "hours, and optimized travel times.\n[PLANNER]"
                )
                logger.info("[PLANNER] appended via post-process fallback — itinerary detected")

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
        extra_system_context: str = "",
    ) -> List[Dict[str, Any]]:
        """Build the full message list for the LLM."""
        system_prompt = build_system_prompt(include_itinerary=(response_style == "detailed"))
        # Inject the current date so the LLM grounds "this week" / "now" /
        # "currently" queries on the real date instead of its training
        # cutoff. Without this, generated Tavily/web-search queries default
        # to the model's knowledge cutoff (observed: "October 2023" for a
        # "this week" query in June 2026).
        from datetime import datetime
        now = datetime.now()
        date_context = (
            f"\n\n## CURRENT DATE CONTEXT\n"
            f"Today's date is {now.strftime('%A, %B %d, %Y')} "
            f"(ISO: {now.strftime('%Y-%m-%d')}). "
            f"Use this date for any 'this week', 'now', 'currently', 'this "
            f"month', or 'upcoming' queries. When you call search_web, "
            f"include the current month and year in the query."
        )
        system_prompt = system_prompt + date_context
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system_prompt}
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

        # Caller-supplied ground-truth / mode instructions (POI_EXPLAIN, etc.).
        # Placed last so it overrides the generic style guidance above.
        if extra_system_context:
            messages.append({"role": "system", "content": extra_system_context})

        # User's actual message
        messages.append({"role": "user", "content": user_message})

        return messages

    # ==================================================================
    # Tool Definitions for LLM
    # ==================================================================

    @staticmethod
    def _get_tool_definitions(include_wikimedia_image: bool = False) -> List[Dict]:
        """Return the tool schemas the LLM can invoke.

        ``include_wikimedia_image`` adds the Wikipedia image-search tool,
        used by POI_EXPLAIN when a POI has no images in the database.
        """
        defs = [
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

        if include_wikimedia_image:
            defs.append({
                "type": "function",
                "function": {
                    "name": "search_wikimedia_image",
                    "description": (
                        "Search Wikipedia for a real, freely-licensed image of a place "
                        "or landmark. Returns an image URL. Call this ONLY when a POI's "
                        "database image_urls list is EMPTY and you need an image to embed. "
                        "Do not call it if image_urls already has URLs."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The place/landmark name to find an image for (e.g. 'Philae Temple')",
                            },
                        },
                        "required": ["query"],
                    },
                },
            })

        return defs

    # ==================================================================
    # Helpers
    # ==================================================================

    @staticmethod
    def _is_recommendation_intent(query: str) -> bool:
        """Detect queries asking for POI suggestions / discoveries.

        These must ground in the POI database via ``search_pois`` (never
        parametric memory) so the region filter + real records apply.
        Triggers on phrases like "hidden gems", "best places", "off the
        beaten path", "recommend", "suggest", "what to see/visit/do",
        "must-see", "worth visiting".
        """
        q = query.lower()
        patterns = [
            r"hidden gems?",
            r"off[- ]?(the[- ]?)?beaten[- ]?path",
            r"\b(best|top|great|cool|nice|amazing|underrated|lesser[- ]?known|secret)\b"
            r".{0,30}\b(places?|spots?|sites?|things|attractions?|destinations?|gems?)\b",
            r"\b(recommend|suggest)\b.{0,40}\b(place|site|spot|thing|visit|see|do)\b",
            r"\bwhat (should|can|to) (i |we )?(visit|see|do|explore)\b",
            r"\bmust[- ]?see\b",
            r"\bworth (visiting|seeing|exploring)\b",
            r"\bwhere (should|can|to).{0,20}\b(go|visit|see|eat|stay)\b",
            # Travel-discovery phrasings that imply "what can I realistically do?"
            # — caught after the 8hr-layover regression: gpt-4o-mini was using
            # get_weather as a fig-leaf then inventing an itinerary from
            # parametric memory. These force search_pois so the real
            # region-filtered records flow.
            r"\b(layover|stopover|transit)\b.{0,40}\b(what|realistic|see|do|visit|explore|worth)\b",
            r"\b\d+[\s\-]?hours?\b.{0,40}\b(layover|stopover|what|realistic|see|do|visit)\b",
        ]
        return any(re.search(p, q) for p in patterns)

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
