"""
VOYO Itinerary Engine Package

Bridges CLEO's creative curation with VROOM's deterministic optimization.
No LLM calls — the engine handles pure logistics (fetch, optimize, enrich, persist).

Components:
  ItineraryEngine    — orchestrates the full optimize → enrich → theme pipeline
  ItineraryPersistence — saves/loads itineraries to/from Supabase
"""

from src.itinerary.engine import ItineraryEngine
from src.itinerary.persistence import ItineraryPersistence

__all__ = ["ItineraryEngine", "ItineraryPersistence"]
