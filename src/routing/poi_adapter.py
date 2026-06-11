"""
VOYO POI Adapter — Transform Supabase POI records into VROOM job definitions

Handles:
- Extracting lat/lng coordinates
- Converting opening_hours JSONB to VROOM time_windows (seconds from midnight)
- Converting average_visit_duration (minutes) to VROOM service time (seconds)
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class POIAdapter:
    """Transform Supabase POI records into VROOM job definitions."""

    def to_vroom_jobs(
        self, pois: List[Dict[str, Any]], location_offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Convert POI records to VROOM job objects.

        Args:
            pois: List of POI dicts from Supabase.
            location_offset: Starting index in the distance matrix.

        Returns:
            List of VROOM job definitions.
        """
        jobs: List[Dict[str, Any]] = []

        for idx, poi in enumerate(pois):
            service_seconds = self._get_service_seconds(poi)

            job: Dict[str, Any] = {
                "id": poi.get("id", idx + 1),
                "location": idx + location_offset,
                "service": service_seconds,
                "description": poi.get("name", f"POI {idx}"),
            }

            time_windows = self.parse_opening_hours_to_seconds(
                poi.get("opening_hours")
            )
            if time_windows:
                job["time_windows"] = time_windows

            jobs.append(job)

        return jobs

    def parse_opening_hours_to_seconds(
        self, hours_jsonb: Any,
    ) -> List[List[int]]:
        """Parse Supabase opening_hours JSONB into VROOM time_windows.

        Input formats handled:
            {"weekday_text": ["Monday: 8:00 AM – 5:00 PM", ...]}
            {"weekday_text": ["Monday: 8:00 AM - 5:00 PM", ...]}
            {"weekday_text": ["Monday: 8:00 – 17:00", ...]}
            None, {}, or missing → returns [] (no constraint)

        Returns:
            List of [open_seconds, close_seconds] pairs.
            For simplicity, returns the most permissive window across all days
            (i.e., earliest open and latest close).
        """
        if not hours_jsonb or not isinstance(hours_jsonb, dict):
            return []

        weekday_text = hours_jsonb.get("weekday_text")
        if not weekday_text or not isinstance(weekday_text, list):
            return []

        earliest_open: Optional[int] = None
        latest_close: Optional[int] = None

        for entry in weekday_text:
            parsed = self._parse_single_day(str(entry))
            if parsed:
                open_s, close_s = parsed
                if earliest_open is None or open_s < earliest_open:
                    earliest_open = open_s
                if latest_close is None or close_s > latest_close:
                    latest_close = close_s

        if earliest_open is not None and latest_close is not None:
            return [[earliest_open, latest_close]]

        return []

    # ==================================================================
    # Internal
    # ==================================================================

    @staticmethod
    def _get_service_seconds(poi: Dict[str, Any]) -> int:
        """Get visit duration in seconds, respecting adjusted duration."""
        if "adjusted_visit_duration" in poi:
            return int(poi["adjusted_visit_duration"]) * 60

        duration_minutes = poi.get("average_visit_duration") or 60
        return int(duration_minutes) * 60

    @staticmethod
    def _parse_single_day(text: str) -> Optional[Tuple[int, int]]:
        """Parse a single weekday_text entry like "Monday: 8:00 AM – 5:00 PM".

        Returns (open_seconds, close_seconds) or None if unparseable.
        """
        # Remove day prefix: "Monday: "
        time_part = re.sub(r"^[A-Za-z]+:\s*", "", text).strip()
        if not time_part:
            return None

        # Handle various separators: "–", "-", "to", "–"
        time_part = time_part.replace("–", "-").replace("—", "-")

        # Pattern 1: 12-hour format with AM/PM
        match_12h = re.match(
            r"(\d{1,2}):(\d{2})\s*(AM|PM)\s*[-–]\s*(\d{1,2}):(\d{2})\s*(AM|PM)",
            time_part,
            re.IGNORECASE,
        )
        if match_12h:
            open_s = POIAdapter._hms_to_seconds(
                int(match_12h.group(1)), int(match_12h.group(2)),
                match_12h.group(3).upper(),
            )
            close_s = POIAdapter._hms_to_seconds(
                int(match_12h.group(4)), int(match_12h.group(5)),
                match_12h.group(6).upper(),
            )
            return (open_s, close_s)

        # Pattern 2: 24-hour format "8:00 – 17:00"
        match_24h = re.match(
            r"(\d{1,2}):(\d{2})\s*[-–]\s*(\d{1,2}):(\d{2})",
            time_part,
        )
        if match_24h:
            open_s = int(match_24h.group(1)) * 3600 + int(match_24h.group(2)) * 60
            close_s = int(match_24h.group(3)) * 3600 + int(match_24h.group(4)) * 60
            return (open_s, close_s)

        # Pattern 3: "Open 24 hours" or "24/7"
        if "24" in time_part.lower():
            return (0, 86400)  # midnight to midnight

        return None

    @staticmethod
    def _hms_to_seconds(hour: int, minute: int, ampm: str) -> int:
        """Convert 12-hour time to seconds from midnight."""
        if ampm == "PM" and hour != 12:
            hour += 12
        elif ampm == "AM" and hour == 12:
            hour = 0
        return hour * 3600 + minute * 60
