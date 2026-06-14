"""
CLEO Chatbot Configuration
Cairo Local Expert & Operator — Configuration & Async Groq Client
"""

import os
import re
import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, AsyncGenerator, Tuple

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()


class CleoConfig:
    """CLEO chatbot configuration — frozen values read from env at import time."""

    # Groq API
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    model: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "8000"))

    # Semantic Cache (Redis)
    enable_cache: bool = True
    cache_ttl: int = 86400  # 24 hours
    cache_db: int = 1

    # Tools
    enable_weather_tool: bool = True
    enable_web_search_tool: bool = True
    enable_supabase_tool: bool = True

    # User Profiling
    enable_profiling: bool = True
    profile_learning: bool = True

    # Conversation Memory
    max_conversation_history: int = 20
    enable_conversation_memory: bool = True

    # Personality
    tone: str = "friendly"
    use_arabic_phrases: bool = True
    use_emojis: bool = True

    # Logging
    debug_mode: bool = False
    log_all_queries: bool = True

    # ReAct loop
    max_agent_iterations: int = 5

    def __init__(self):
        if not self.groq_api_key:
            logger.warning("GROQ_API_KEY not found in environment variables")


config = CleoConfig()


# ---------------------------------------------------------------------------
# LLM Response dataclass
# ---------------------------------------------------------------------------

class LLMResponse:
    """Structured result from a single Groq completion call."""

    def __init__(self, content: Optional[str], tool_calls: Optional[list] = None,
                 finish_reason: Optional[str] = None):
        self.content = content
        self.tool_calls = tool_calls  # list of ChatCompletionMessageToolCall
        self.finish_reason = finish_reason

    @property
    def has_tool_calls(self) -> bool:
        return bool(self.tool_calls)

    def to_message(self) -> Dict[str, Any]:
        """Return the assistant message dict to append to the messages list.

        When the LLM made tool calls we include them so the conversation
        history is complete for the next iteration.
        """
        msg: Dict[str, Any] = {"role": "assistant"}
        if self.content:
            msg["content"] = self.content
        if self.tool_calls:
            serialised = []
            for tc in self.tool_calls:
                # Groq SDK returns objects with ``.id`` / ``.function``;
                # if for some reason we get a plain dict, pass it through.
                if isinstance(tc, dict):
                    serialised.append(tc)
                else:
                    serialised.append({
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    })
            msg["tool_calls"] = serialised
        return msg


# ---------------------------------------------------------------------------
# Native tool-call recovery (Llama-3 native XML format → structured)
# ---------------------------------------------------------------------------
#
# `llama-3.3-70b-versatile` intermittently emits tool calls in its NATIVE
# XML format — `<function=NAME{ARGS}></function>` — inside `content`, instead
# of the structured `tool_calls` object the OpenAI/Groq schema expects. Groq's
# server rejects this with HTTP 400 but helpfully returns the raw text in the
# error body's `failed_generation` field (its documented recovery hook).
#
# The code below parses that leaked format into a real `tool_calls` response
# so the agent loop proceeds. This makes CLEO robust to the model's format
# instability WITHOUT downgrading the model or disabling tools.


@dataclass
class _RecoveredFunction:
    """Mimics the groq SDK function-call object: name + arguments (JSON str)."""
    name: str
    arguments: str


@dataclass
class _RecoveredToolCall:
    """Mimics the groq SDK ``ChatCompletionMessageToolCall``.

    Satisfies both ``LLMResponse.to_message()`` (object branch) and the
    agent loop's attribute access (``tc.function.name`` / ``tc.id`` /
    ``tc.function.arguments``).
    """
    id: str
    function: _RecoveredFunction
    type: str = "function"


def _extract_failed_generation(exc: Exception) -> Optional[str]:
    """Pull Groq's ``failed_generation`` text out of a 400 ``BadRequestError``.

    Tries the parsed JSON body the SDK attaches to the exception first, then
    falls back to scraping the string repr. Returns ``None`` if not present.
    """
    # The groq/openai SDKs attach the parsed JSON body under different
    # attribute names across versions.
    for attr in ("body", "api_response", "response"):
        body = getattr(exc, attr, None)
        if isinstance(body, dict):
            err = body.get("error", body)
            if isinstance(err, dict) and err.get("failed_generation"):
                return err["failed_generation"]
    # Fallback: best-effort scrape of the raw tags from the string repr.
    m = re.search(r"(<function=.*</function>)", str(exc), re.DOTALL)
    return m.group(1) if m else None


def _parse_native_tool_calls(text: str) -> List[Tuple[str, str]]:
    """Parse Llama-3 native tool-call tags into ``(name, args_json_str)`` pairs.

    Handles both observed Llama-3 wire formats robustly:
      * ``<function=NAME>{ARGS}</function>``  (proper XML — ``>`` before args)
      * ``<function=NAME{ARGS}></function>``  (compact — no ``>`` before args)
    The function name is matched as a ``\w+`` token so any stray ``>`` or
    whitespace between the name and the JSON args is never captured into the
    name. Brace balancing with string awareness handles nested JSON.
    """
    calls: List[Tuple[str, str]] = []
    i = 0
    while True:
        start = text.find("<function=", i)
        if start == -1:
            break
        # Name is the \\w+ token immediately after "<function=".
        name_match = re.match(r"<function=(\w+)", text[start:])
        if not name_match:
            break
        name = name_match.group(1)
        brace_start = text.find("{", start + len("<function=") + len(name))
        if brace_start == -1:
            break
        # Walk to the matching close brace, respecting strings + nesting.
        depth = 0
        j = brace_start
        in_str = False
        escaped = False
        while j < len(text):
            ch = text[j]
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_str = not in_str
            elif not in_str:
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        break
            j += 1
        if depth != 0:
            break  # unbalanced braces — bail rather than guess
        raw_args = text[brace_start:j + 1]
        try:
            json.loads(raw_args)  # validate
            args_str = raw_args
        except json.JSONDecodeError:
            args_str = "{}"
        if name:
            calls.append((name, args_str))
        i = j + 1
    return calls


def _recover_tool_call_response(exc: Exception) -> Optional["LLMResponse"]:
    """Recover a structured ``LLMResponse`` from a native-format tool-call leak.

    When the model emits `<function=NAME{ARGS}></function>` and Groq rejects
    it with a 400, this rebuilds the intended tool call(s) as a proper
    ``tool_calls`` response so the agent loop executes them. The model HAS
    decided what to call — only the wire format was wrong — so no retry is
    needed and no generic 'trouble connecting' message is shown.

    Returns ``None`` when the exception is not a recoverable tool-call leak
    (so callers fall through to their normal retry / error handling).
    """
    failed = _extract_failed_generation(exc)
    if not failed or "<function=" not in failed:
        return None
    parsed = _parse_native_tool_calls(failed)
    if not parsed:
        return None
    tool_calls = [
        _RecoveredToolCall(
            id=f"call_recovered_{i}",
            function=_RecoveredFunction(name=name, arguments=args),
        )
        for i, (name, args) in enumerate(parsed)
    ]
    logger.info(
        "[GROQ] Recovered %d native-format tool call(s) from failed_generation: %s",
        len(tool_calls),
        ", ".join(tc.function.name for tc in tool_calls),
    )
    return LLMResponse(content=None, tool_calls=tool_calls, finish_reason="tool_calls")


# ---------------------------------------------------------------------------
# Async Groq Client
# ---------------------------------------------------------------------------

class GroqClient:
    """Async Groq API client for CLEO.

    Uses ``groq.AsyncGroq`` so every call is awaitable and never blocks
    the FastAPI event loop.  A synchronous fallback is provided for
    non-async callers (tests, scripts).
    """

    def __init__(self):
        if not config.groq_api_key:
            raise ValueError(
                "GROQ_API_KEY not found in environment variables. "
                "Please add it to your .env file."
            )
        try:
            from groq import AsyncGroq
            self.async_client = AsyncGroq(api_key=config.groq_api_key)
            # Also keep a sync client for non-async callers
            from groq import Groq
            self.sync_client = Groq(api_key=config.groq_api_key)
            self.model = config.model
            logger.info(f"Groq client initialized with model: {self.model}")
        except ImportError:
            raise ImportError("groq package not installed. Run: pip install groq")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            raise

    # ------------------------------------------------------------------
    # Async API (primary — used by FastAPI endpoints)
    # ------------------------------------------------------------------

    async def generate_async(
        self,
        messages: list,
        tools: Optional[list] = None,
        temperature: Optional[float] = None,
    ) -> LLMResponse:
        """Async Groq call with retry logic.

        Returns an ``LLMResponse`` that may contain tool calls, plain
        text, or both.
        """
        max_retries = 3
        last_error: Optional[Exception] = None

        for attempt in range(max_retries):
            try:
                params: Dict[str, Any] = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature or config.temperature,
                    "max_tokens": config.max_tokens,
                }
                if tools:
                    params["tools"] = tools
                    params["tool_choice"] = "auto"

                response = await self.async_client.chat.completions.create(**params)
                message = response.choices[0].message

                return LLMResponse(
                    content=message.content,
                    tool_calls=message.tool_calls if hasattr(message, "tool_calls") and message.tool_calls else None,
                    finish_reason=response.choices[0].finish_reason,
                )

            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                error_type = type(e).__name__.lower()
                logger.warning(f"[GROQ ERROR] attempt {attempt + 1}/{max_retries} — {type(e).__name__}: {e}")

                # RECOVER: Llama-3 native tool-call format leak (HTTP 400
                # carrying `failed_generation`). The model HAS decided which
                # tool to call; Groq only rejected its wire format. Parse and
                # proceed — no retry needed.
                recovered = _recover_tool_call_response(e)
                if recovered is not None:
                    return recovered

                is_retryable = (
                    "rate_limit" in error_type
                    or "rate limit" in error_str
                    or "429" in error_str
                    or "503" in error_str
                    or "502" in error_str
                    or "timeout" in error_str
                    or "connection" in error_str
                )
                if is_retryable and attempt < max_retries - 1:
                    wait = 2 ** attempt
                    logger.info(f"[GROQ] Retrying in {wait}s...")
                    await asyncio.sleep(wait)
                    continue
                break

        logger.error(f"Groq generate_async failed after {max_retries} attempts: {last_error}")
        return LLMResponse(
            content="I apologize, but I'm having trouble connecting right now. Please try again in a moment."
        )

    async def generate_streaming(
        self,
        messages: list,
        tools: Optional[list] = None,
        temperature: Optional[float] = None,
    ) -> AsyncGenerator[str, None]:
        """Yield response chunks for SSE streaming to the frontend.

        Tool calls are NOT supported in streaming mode — if the LLM
        decides to call tools the first chunk will contain a flag and
        the caller should fall back to ``generate_async``.
        """
        params: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or config.temperature,
            "max_tokens": config.max_tokens,
            "stream": True,
        }
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"

        try:
            stream = await self.async_client.chat.completions.create(**params)
            async for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content
                # If tool calls come through streaming, signal caller
                if hasattr(delta, "tool_calls") and delta.tool_calls:
                    # Streaming tool calls are complex; fall back
                    return
        except Exception as e:
            logger.error(f"Groq streaming error: {e}")
            yield "[Error streaming response]"

    # ------------------------------------------------------------------
    # Sync API (fallback for scripts / tests)
    # ------------------------------------------------------------------

    def generate(self, messages: list, tools: Optional[list] = None) -> Any:
        """Synchronous Groq call (legacy compatibility).

        Prefer ``generate_async`` in async contexts.
        """
        max_retries = 3
        last_error: Optional[Exception] = None

        import time
        for attempt in range(max_retries):
            try:
                params = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": config.temperature,
                    "max_tokens": config.max_tokens,
                }
                if tools:
                    params["tools"] = tools
                    params["tool_choice"] = "auto"

                response = self.sync_client.chat.completions.create(**params)
                message = response.choices[0].message

                if hasattr(message, "tool_calls") and message.tool_calls:
                    return {
                        "content": message.content,
                        "tool_calls": message.tool_calls,
                        "finish_reason": response.choices[0].finish_reason,
                    }
                return message.content

            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                logger.warning(f"[GROQ ERROR] attempt {attempt + 1}/{max_retries} — {type(e).__name__}: {e}")

                # RECOVER: Llama-3 native tool-call format leak (HTTP 400
                # carrying `failed_generation`). See `generate_async`.
                recovered = _recover_tool_call_response(e)
                if recovered is not None:
                    return {
                        "content": recovered.content,
                        "tool_calls": recovered.tool_calls,
                        "finish_reason": recovered.finish_reason,
                    }

                is_retryable = (
                    "429" in error_str
                    or "503" in error_str
                    or "502" in error_str
                    or "timeout" in error_str
                    or "connection" in error_str
                )
                if is_retryable and attempt < max_retries - 1:
                    wait = 2 ** attempt
                    logger.info(f"[GROQ] Retrying in {wait}s...")
                    time.sleep(wait)
                    continue
                break

        logger.error(f"Groq generate failed after {max_retries} attempts: {last_error}")
        return "I apologize, but I'm having trouble connecting right now. Please try again in a moment."

    async def test_connection(self) -> bool:
        """Test Groq API connection (async)."""
        try:
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10,
            )
            logger.info("Groq API connection test successful")
            return True
        except Exception as e:
            logger.error(f"Groq API connection test failed: {e}")
            return False
