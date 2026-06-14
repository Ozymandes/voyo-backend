"""
Wikimedia Image Search Tool for CLEO
Find a representative image for a POI name via the MediaWiki API.

Uses the ``generator=search`` + ``pageimages`` Action API on English
Wikipedia — **no API key required**.  The request pattern (User-Agent
header, ``requests``, exponential-backoff retry) mirrors
``rebuild_database.py:wikimedia_fetch``.
"""

import logging
import time
from typing import Dict, Optional

import requests

logger = logging.getLogger(__name__)

WIKI_API = "https://en.wikipedia.org/w/api.php"
UA = {"User-Agent": "VoyoApp/1.0 (educational thesis project)"}


class WikimediaImageTool:
    """Find a Wikipedia image for a POI using ``generator=search`` +
    ``pageimages``.

    The MediaWiki Action API performs a relevance search for ``query``
    (``generator=search``) and, for the top pages, returns the lead image
    via the ``pageimages`` prop (``piprop=thumbnail|original``).  No API
    key is needed.
    """

    def search_image(self, query: str, thumb_size: int = 800) -> Dict:
        """Search Wikipedia for ``query`` and return the top result's image.

        Returns a dict::

            {
              "query": "...",
              "title": "Great Pyramid of Giza",
              "image_url": "https://upload.wikimedia.org/...",   # original
              "thumbnail_url": "https://upload.wikimedia.org/...", # sized
              "source_page": "https://en.wikipedia.org/wiki/...",
            }

        ``image_url`` is ``None`` when no image is available (so callers
        can degrade gracefully).
        """
        query = (query or "").strip()
        empty = {
            "query": query,
            "title": None,
            "image_url": None,
            "thumbnail_url": None,
            "source_page": None,
        }
        if not query:
            return empty

        try:
            data = self._query(query, thumb_size=thumb_size, tries=3)
        except Exception as e:
            logger.error(f"Wikimedia image search failed for '{query}': {e}")
            empty["error"] = str(e)
            return empty

        pages = (data.get("query", {}) or {}).get("pages", {}) or {}
        if not pages:
            logger.info(f"Wikimedia search returned no pages for '{query}'")
            return empty

        # ``generator=search`` annotates each page with an ``index`` (rank).
        # Pick the best-ranked page that actually has an image.
        ranked = sorted(
            pages.values(),
            key=lambda p: p.get("index", 1_000_000),
        )
        best = next((p for p in ranked if (p.get("original") or p.get("thumbnail"))), None)
        if best is None:
            best = ranked[0]

        title = best.get("title")
        original = (best.get("original") or {}).get("source")
        thumb = (best.get("thumbnail") or {}).get("source")
        source_page = (
            f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
            if title else None
        )

        return {
            "query": query,
            "title": title,
            "image_url": original or thumb,
            "thumbnail_url": thumb,
            "source_page": source_page,
        }

    async def search_image_async(self, query: str, thumb_size: int = 800) -> Dict:
        """Async wrapper — runs the sync search in a thread."""
        import asyncio
        return await asyncio.to_thread(self.search_image, query, thumb_size)

    # ------------------------------------------------------------------

    @staticmethod
    def _query(query: str, thumb_size: int = 800, tries: int = 3) -> Dict:
        """Call the MediaWiki API with retry (mirrors ``wikimedia_fetch``)."""
        params = {
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": query,
            "gsrlimit": "3",          # a few candidates so we can pick one with an image
            "prop": "pageimages",
            "piprop": "thumbnail|original",
            "pithumbsize": str(thumb_size),
        }
        last_exc: Optional[Exception] = None
        for attempt in range(tries):
            try:
                r = requests.get(WIKI_API, params=params, headers=UA, timeout=12)
                r.raise_for_status()
                return r.json()
            except Exception as e:
                last_exc = e
                time.sleep(1.0 * (2 ** attempt))
        raise last_exc  # type: ignore[misc]
