"""
CLEO Conversation Memory — Supabase-Backed with Auto-Summarization

Old messages (beyond the recent window) are compressed into a short
summary paragraph and stored as a single ``system`` row.  This keeps
the LLM context window lean while preserving conversational continuity.

Lifecycle:
  messages 1..N-20  →  summarized into a single "context" row
  messages N-20..N  →  kept as individual rows (recent window)
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from src.database.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)

# How many recent messages to keep verbatim before summarizing older ones
SUMMARY_THRESHOLD = 20


class ConversationMemory:
    """Supabase-backed conversation history with auto-summarization."""

    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self.db = SupabaseClient()
        logger.info(
            f"Conversation memory initialized (Supabase-backed, "
            f"max_history={max_history}, summarize_after={SUMMARY_THRESHOLD})"
        )

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def add_message(
        self,
        user_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None,
    ):
        """Store one message in Supabase.

        Falls back silently if the DB write fails so the agent never
        crashes on a persistence error.
        """
        row = {
            "user_id": user_id,
            "role": role,
            "content": content,
            "metadata": metadata or {},
        }
        try:
            self.db.insert_record("conversation_messages", row, use_admin=True)
            logger.debug(f"Persisted {role} message for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to persist message to Supabase: {e}")

    async def add_message_async(
        self,
        user_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None,
    ):
        """Async wrapper — runs the insert in a thread."""
        import asyncio
        await asyncio.to_thread(self.add_message, user_id, role, content, metadata)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_history(
        self,
        user_id: str,
        last_n: Optional[int] = None,
    ) -> List[Dict]:
        """Return raw message dicts for a user, oldest-first."""
        limit = last_n or self.max_history
        try:
            rows = self.db.get_records(
                "conversation_messages",
                filters={"user_id": user_id},
                use_admin=True,
                limit=limit,
            )
            rows.sort(key=lambda m: m.get("created_at", ""))
            return rows
        except Exception as e:
            logger.error(f"Error loading conversation history: {e}")
            return []

    def get_context(self, user_id: str, last_n: int = 10) -> str:
        """Return a formatted conversation string suitable for LLM injection.

        If older messages have been summarized, prepends the summary
        before the recent window.
        """
        all_rows = self._get_all_rows(user_id)

        if not all_rows:
            return ""

        # Find a summary row if one exists
        summary_row = None
        message_rows: List[Dict] = []
        for row in all_rows:
            meta = row.get("metadata", {})
            if isinstance(meta, dict) and meta.get("is_summary"):
                summary_row = row
            else:
                message_rows.append(row)

        parts: List[str] = []

        # Prepend summary of older conversation
        if summary_row:
            parts.append(f"[Earlier conversation summary]: {summary_row['content']}")

        # Add recent messages (oldest → newest)
        message_rows.sort(key=lambda m: m.get("created_at", ""))
        recent = message_rows[-last_n:]
        for msg in recent:
            role = "You" if msg["role"] == "user" else "CLEO"
            parts.append(f"{role}: {msg['content']}")

        return "\n".join(parts)

    def get_messages(self, user_id: str, last_n: int = 20) -> List[Dict]:
        """Return messages as ``{role, content}`` dicts for the LLM message list.

        Includes a system summary row at the start if older messages
        were compressed.
        """
        all_rows = self._get_all_rows(user_id)

        summary_row = None
        message_rows: List[Dict] = []
        for row in all_rows:
            meta = row.get("metadata", {})
            if isinstance(meta, dict) and meta.get("is_summary"):
                summary_row = row
            else:
                message_rows.append(row)

        result: List[Dict] = []

        if summary_row:
            result.append({
                "role": "system",
                "content": f"[Earlier conversation summary]: {summary_row['content']}",
            })

        message_rows.sort(key=lambda m: m.get("created_at", ""))
        for r in message_rows[-last_n:]:
            result.append({"role": r["role"], "content": r["content"]})

        return result

    # ------------------------------------------------------------------
    # Summarization
    # ------------------------------------------------------------------

    def maybe_summarize(self, user_id: str) -> bool:
        """Check if old messages should be compressed.  If the user has
        more than ``SUMMARY_THRESHOLD`` individual messages, summarize
        the oldest half into a single row.

        Returns True if summarization was performed.
        """
        try:
            all_rows = self._get_all_rows(user_id)
            # Filter out any existing summary row
            message_rows = [
                r for r in all_rows
                if not (isinstance(r.get("metadata", {}), dict) and r["metadata"].get("is_summary"))
            ]

            if len(message_rows) <= SUMMARY_THRESHOLD:
                return False

            logger.info(
                f"User {user_id} has {len(message_rows)} messages — summarizing old ones"
            )

            # Split: oldest half → summarize, recent half → keep
            split_point = len(message_rows) // 2
            old_rows = message_rows[:split_point]
            keep_rows = message_rows[split_point:]

            # Build summary text
            summary_text = self._build_summary(old_rows)

            # Delete old rows
            old_ids = [r["id"] for r in old_rows]
            for old_id in old_ids:
                try:
                    self.db.admin_client.table("conversation_messages").delete().eq(
                        "id", old_id
                    ).execute()
                except Exception:
                    pass

            # Delete any existing summary row
            try:
                self.db.admin_client.table("conversation_messages").delete().eq(
                    "user_id", user_id
                ).eq("metadata->>is_summary", "true").execute()
            except Exception:
                pass

            # Insert new summary row
            self.db.insert_record(
                "conversation_messages",
                {
                    "user_id": user_id,
                    "role": "system",
                    "content": summary_text,
                    "metadata": {"is_summary": True, "summarized_count": len(old_rows)},
                },
                use_admin=True,
            )

            logger.info(
                f"Summarized {len(old_rows)} old messages for user {user_id}. "
                f"Kept {len(keep_rows)} recent."
            )
            return True

        except Exception as e:
            logger.error(f"Error during summarization for user {user_id}: {e}")
            return False

    async def maybe_summarize_async(self, user_id: str) -> bool:
        """Async wrapper for summarization."""
        import asyncio
        return await asyncio.to_thread(self.maybe_summarize, user_id)

    @staticmethod
    def _build_summary(rows: List[Dict]) -> str:
        """Build a concise text summary from a list of message rows.

        Extracts key topics (POIs, regions, preferences) mentioned in
        the conversation without needing an LLM call.
        """
        pois_mentioned: set = set()
        regions_mentioned: set = set()
        topics: List[str] = []
        preferences: List[str] = []

        # Known regions and categories for extraction
        known_regions = {
            "cairo", "giza", "alexandria", "luxor", "aswan",
            "hurghada", "sinai", "sharm el sheikh", "marsa alam",
            "dahab", "nuweiba",
        }
        known_categories = {
            "historical", "cultural", "religious", "natural",
            "entertainment", "museum", "mosque", "church",
            "temple", "pyramid", "market", "bazaar",
        }

        for row in rows:
            content = (row.get("content") or "").lower()

            for region in known_regions:
                if region in content and region not in regions_mentioned:
                    regions_mentioned.add(region)

            for cat in known_categories:
                if cat in content:
                    topics.append(cat)

            # Extract explicit preferences
            pref_words = ["love", "hate", "prefer", "enjoy", "like", "budget", "luxury", "family"]
            if any(w in content for w in pref_words) and row["role"] == "user":
                # Take the first 80 chars as a preference signal
                preferences.append(row["content"][:80])

        parts: List[str] = []
        if regions_mentioned:
            parts.append(f"Regions discussed: {', '.join(sorted(regions_mentioned))}")
        if topics:
            unique_topics = list(dict.fromkeys(topics))[:5]  # top 5 unique
            parts.append(f"Topics: {', '.join(unique_topics)}")
        if preferences:
            parts.append("User preferences mentioned:")
            for pref in preferences[:3]:
                parts.append(f'  - "{pref}"')

        if not parts:
            return f"Previous conversation with {len(rows)} messages covering general Egypt travel questions."

        return ". ".join(parts) + "."

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_all_rows(self, user_id: str) -> List[Dict]:
        """Fetch all conversation rows for a user (no limit)."""
        try:
            # Fetch a generous upper bound — conversations shouldn't exceed this
            rows = self.db.get_records(
                "conversation_messages",
                filters={"user_id": user_id},
                use_admin=True,
                limit=500,
            )
            return rows
        except Exception as e:
            logger.error(f"Error fetching all rows for user {user_id}: {e}")
            return []

    # ------------------------------------------------------------------
    # Stats / maintenance
    # ------------------------------------------------------------------

    def get_conversation_stats(self, user_id: str) -> Dict:
        """Return basic stats about a user's conversation."""
        history = self._get_all_rows(user_id)
        message_rows = [
            r for r in history
            if not (isinstance(r.get("metadata", {}), dict) and r["metadata"].get("is_summary"))
        ]
        if not message_rows:
            return {
                "total_messages": 0,
                "user_messages": 0,
                "assistant_messages": 0,
                "first_message": None,
                "last_message": None,
                "has_summary": any(
                    isinstance(r.get("metadata", {}), dict) and r["metadata"].get("is_summary")
                    for r in history
                ),
            }
        user_msgs = [m for m in message_rows if m["role"] == "user"]
        assistant_msgs = [m for m in message_rows if m["role"] == "assistant"]
        return {
            "total_messages": len(message_rows),
            "user_messages": len(user_msgs),
            "assistant_messages": len(assistant_msgs),
            "first_message": message_rows[0].get("created_at"),
            "last_message": message_rows[-1].get("created_at"),
            "has_summary": any(
                isinstance(r.get("metadata", {}), dict) and r["metadata"].get("is_summary")
                for r in history
            ),
        }

    def clear_user_history(self, user_id: str):
        """Delete all conversation rows for a user."""
        try:
            self.db.admin_client.table("conversation_messages").delete().eq(
                "user_id", user_id
            ).execute()
            logger.info(f"Cleared conversation history for user {user_id}")
        except Exception as e:
            logger.error(f"Error clearing history for user {user_id}: {e}")

    def clear_old_conversations(self, days: int = 7):
        """Delete conversations older than ``days`` days."""
        try:
            from datetime import timedelta
            cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
            self.db.admin_client.table("conversation_messages").delete().lt(
                "created_at", cutoff
            ).execute()
            logger.info(f"Cleared conversations older than {days} days")
        except Exception as e:
            logger.error(f"Error clearing old conversations: {e}")

    def extract_entities(self, user_id: str) -> Dict:
        """Placeholder — returns empty entity dict."""
        return {"pois": [], "regions": [], "categories": [], "preferences": {}}

    def summarize_conversation(self, user_id: str) -> str:
        """Return a text summary of recent conversation topics."""
        rows = self._get_all_rows(user_id)
        message_rows = [
            r for r in rows
            if not (isinstance(r.get("metadata", {}), dict) and r["metadata"].get("is_summary"))
        ]
        if not message_rows:
            return ""
        return self._build_summary(message_rows)
