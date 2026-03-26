"""
Conversation Memory for CLEO
Track multi-turn conversations and context
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ConversationMemory:
    """Manage conversation history and context for multi-turn conversations"""

    def __init__(self, max_history: int = 20):
        """
        Initialize conversation memory

        Args:
            max_history: Maximum number of messages to remember per user
        """
        self.max_history = max_history
        self.conversations: Dict[str, List[Dict]] = {}
        logger.info(f"Conversation memory initialized (max_history={max_history})")

    def add_message(
        self,
        user_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """
        Add message to conversation history

        Args:
            user_id: User identifier
            role: Message role ("user" or "assistant")
            content: Message content
            metadata: Optional metadata (timestamp, tools used, etc.)
        """
        if user_id not in self.conversations:
            self.conversations[user_id] = []

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        self.conversations[user_id].append(message)

        # Trim to max history
        if len(self.conversations[user_id]) > self.max_history:
            self.conversations[user_id] = self.conversations[user_id][-self.max_history:]

        logger.debug(f"Added {role} message for user {user_id} "
                    f"(total: {len(self.conversations[user_id])})")

    def get_history(
        self,
        user_id: str,
        last_n: Optional[int] = None
    ) -> List[Dict]:
        """
        Get conversation history for user

        Args:
            user_id: User identifier
            last_n: Return only last N messages (if specified)

        Returns:
            List of message dictionaries
        """
        history = self.conversations.get(user_id, [])

        if last_n:
            return history[-last_n:]

        return history

    def get_context(
        self,
        user_id: str,
        last_n: int = 10
    ) -> str:
        """
        Get formatted context for LLM

        Args:
            user_id: User identifier
            last_n: Number of recent messages to include

        Returns:
            Formatted conversation context string
        """
        history = self.get_history(user_id, last_n)

        if not history:
            return ""

        context_parts = []
        for msg in history:
            role = "You" if msg["role"] == "user" else "CLEO"
            context_parts.append(f"{role}: {msg['content']}")

        return "\n".join(context_parts)

    def extract_entities(self, user_id: str) -> Dict:
        """
        Extract entities mentioned in conversation

        Args:
            user_id: User identifier

        Returns:
            Dictionary with extracted entities (POIs, regions, preferences, etc.)
        """
        history = self.get_history(user_id, last_n=20)

        entities = {
            "pois": set(),
            "regions": set(),
            "categories": set(),
            "preferences": {}
        }

        # Simple extraction (can be enhanced with NLP)
        for msg in history:
            content = msg["content"].lower()

            # Extract known POI names (would need database lookup)
            # Extract region names
            # Extract category mentions
            # Track preferences

        return {
            k: list(v) if isinstance(v, set) else v
            for k, v in entities.items()
        }

    def clear_old_conversations(self, days: int = 7):
        """
        Clear conversations older than X days

        Args:
            days: Number of days after which to clear conversations
        """
        cutoff = datetime.now() - timedelta(days=days)
        cleared = 0

        for user_id in list(self.conversations.keys()):
            self.conversations[user_id] = [
                msg for msg in self.conversations[user_id]
                if datetime.fromisoformat(msg["timestamp"]) > cutoff
            ]

            # Remove empty conversations
            if not self.conversations[user_id]:
                del self.conversations[user_id]
                cleared += 1

        logger.info(f"Cleared {cleared} old conversations (older than {days} days)")

    def summarize_conversation(self, user_id: str) -> str:
        """
        Generate summary of conversation

        Args:
            user_id: User identifier

        Returns:
            Conversation summary
        """
        history = self.get_history(user_id, last_n=50)

        if not history:
            return ""

        # Extract key points
        pois_discussed = set()
        regions_discussed = set()
        topics = []

        for msg in history:
            content = msg["content"].lower()
            # Extract POIs, regions, topics
            # (Would need NLP for accurate extraction)

        summary_parts = []
        if pois_discussed:
            summary_parts.append(f"Discussed: {', '.join(pois_discussed)}")
        if regions_discussed:
            summary_parts.append(f"Regions: {', '.join(regions_discussed)}")

        return ". ".join(summary_parts) if summary_parts else "General conversation"

    def get_conversation_stats(self, user_id: str) -> Dict:
        """
        Get statistics about user's conversation

        Args:
            user_id: User identifier

        Returns:
            Dictionary with conversation statistics
        """
        history = self.get_history(user_id)

        if not history:
            return {
                "total_messages": 0,
                "user_messages": 0,
                "assistant_messages": 0,
                "first_message": None,
                "last_message": None
            }

        user_messages = [m for m in history if m["role"] == "user"]
        assistant_messages = [m for m in history if m["role"] == "assistant"]

        return {
            "total_messages": len(history),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "first_message": history[0]["timestamp"],
            "last_message": history[-1]["timestamp"]
        }

    def clear_user_history(self, user_id: str):
        """
        Clear conversation history for specific user

        Args:
            user_id: User identifier
        """
        if user_id in self.conversations:
            del self.conversations[user_id]
            logger.info(f"Cleared conversation history for user {user_id}")
