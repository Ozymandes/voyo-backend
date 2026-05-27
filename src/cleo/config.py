"""
CLEO Chatbot Configuration
Cairo Local Expert & Operator - Configuration Settings
"""

import os
from typing import Literal
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class CleoConfig:
    """CLEO chatbot configuration"""

    # Groq API Configuration
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    model: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "8000"))

    # Semantic Cache (Redis)
    enable_cache: bool = True
    cache_ttl: int = 86400  # 24 hours
    cache_db: int = 1  # Use Redis DB 1 (separate from pipeline)

    # Tools
    enable_weather_tool: bool = True
    enable_web_search_tool: bool = True
    enable_supabase_tool: bool = True

    # User Profiling
    enable_profiling: bool = True
    profile_learning: bool = True  # Learn from interactions

    # Conversation Memory
    max_conversation_history: int = 20  # Messages to remember
    enable_conversation_memory: bool = True

    # Personality
    tone: str = "friendly"
    use_arabic_phrases: bool = True
    use_emojis: bool = True

    # Logging
    debug_mode: bool = False
    log_all_queries: bool = True

    def __init__(self):
        """Initialize configuration"""
        if not self.groq_api_key:
            logger.warning("GROQ_API_KEY not found in environment variables")

# Global config instance
config = CleoConfig()


class GroqClient:
    """Groq API client for CLEO"""

    def __init__(self):
        """Initialize Groq client"""
        if not config.groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables. "
                           "Please add it to your .env file.")

        try:
            from groq import Groq
            self.client = Groq(api_key=config.groq_api_key)
            self.model = config.model
            logger.info(f"Groq client initialized with model: {self.model}")
        except ImportError:
            raise ImportError("groq package not installed. "
                            "Run: pip install groq")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            raise

    def generate(self, messages: list, tools: list = None) -> str:
        """
        Generate response using Groq's Llama 3.3 70B

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            tools: Optional list of tool definitions for function calling

        Returns:
            str or dict: Generated response text or dict with tool_calls
        """
        import time

        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                params = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": config.temperature,
                    "max_tokens": config.max_tokens
                }

                if tools:
                    params["tools"] = tools

                response = self.client.chat.completions.create(**params)

                # Handle tool calls - Groq returns ChatCompletion object
                message = response.choices[0].message

                if message.tool_calls:
                    return {
                        "content": message.content,
                        "tool_calls": message.tool_calls,
                        "finish_reason": response.choices[0].finish_reason
                    }

                return message.content

            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                error_type = type(e).__name__.lower()
                print(f"[GROQ ERROR] attempt {attempt + 1}/{max_retries} — {type(e).__name__}: {e}")

                # Retry on rate limit or transient server errors
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
                    wait = 2 ** attempt  # 1 s, 2 s
                    print(f"[GROQ] Retrying in {wait}s...")
                    time.sleep(wait)
                    continue

                # Non-retryable error — break immediately
                break

        logger.error(f"Groq generate failed after {max_retries} attempts: {last_error}")
        return "I apologize, but I'm having trouble connecting right now. Please try again in a moment."

    def test_connection(self) -> bool:
        """Test Groq API connection"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            logger.info("Groq API connection test successful")
            return True
        except Exception as e:
            logger.error(f"Groq API connection test failed: {e}")
            return False
