"""
VOYO Database Schema
Based on CSAI 490-PRD requirements
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid
from sqlalchemy.dialects.postgresql import UUID


Base = declarative_base()

# Enums for categorical data
class Language(enum.Enum):
    ARABIC = "arabic"
    ENGLISH = "english"
    FRENCH = "french"
    SPANISH = "spanish"

class POICategory(enum.Enum):
    HISTORICAL = "historical"
    CULTURAL = "cultural"
    NATURAL = "natural"
    ENTERTAINMENT = "entertainment"
    RELIGIOUS = "religious"
    SHOPPING = "shopping"
    DINING = "dining"
    ACCOMMODATION = "accommodation"
    TRANSPORTATION = "transportation"
    SERVICES = "services"

class AccessibilityType(enum.Enum):
    WHEELCHAIR_ACCESSIBLE = "wheelchair_accessible"
    VISUAL_IMPAIRMENT_SUPPORT = "visual_impairment_support"
    HEARING_IMPAIRMENT_SUPPORT = "hearing_impairment_support"
    MOBILITY_ASSISTANCE = "mobility_assistance"

class AgeRangeType(enum.Enum):
    R18_24 = "18-24"
    R25_34 = "25-34"
    R35_44 = "35-44"
    R45_54 = "45-54"
    R55_64 = "55-64"
    R65_PLUS = "65+"

class ItineraryPaceType(enum.Enum):
    PACKED = "packed_schedule"
    BALANCED = "balanced"
    SLOW = "slow_flexible"

class PlanningStyleType(enum.Enum):
    PLANNED = "everything_pre_planned"
    MIXED = "mix_of_planned_spontaneous"
    SPONTANEOUS = "mostly_spontaneous"

# Core Tables
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    phone_number = Column(String(20))
    profile_image_url = Column(String(500))
    language_preference = Column(Enum(Language), default=Language.ENGLISH)
    nationality = Column(String(50))
    registration_date = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)

    # Relationships
    preferences = relationship("UserPreferences", back_populates="user")
    travel_plans = relationship("TravelPlan", back_populates="user")
    saved_items = relationship("SavedItem", back_populates="user")
    ratings = relationship("UserRating", back_populates="user")

class Region(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    country = Column(String(50), default="Egypt")
    description = Column(Text)
    capital_city = Column(String(100))
    timezone = Column(String(50), default="Africa/Cairo")
    is_active = Column(Boolean, default=True)

    # Relationships
    pois = relationship("POI", back_populates="region")

class POI(Base):
    __tablename__ = "pois"

    id = Column(Integer, primary_key=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    name = Column(String(200), nullable=False)
    name_arabic = Column(String(200))
    description = Column(Text)
    category = Column(Enum(POICategory), nullable=False)

    # Location information
    address = Column(String(500))
    latitude = Column(Float)
    longitude = Column(Float)
    city = Column(String(100))

    # Contact information
    phone_number = Column(String(30))
    website_url = Column(String(500))

    # Operating information
    opening_hours = Column(JSON)  # Store as structured JSON
    ticket_price = Column(Float)
    currency = Column(String(3), default="EGP")
    average_visit_duration = Column(Integer)  # in minutes
    best_visit_times = Column(JSON)  # Store seasons/months

    # Ratings and popularity
    average_rating = Column(Float)
    total_reviews = Column(Integer, default=0)
    popularity_score = Column(Float, default=0)

    # Media
    image_urls = Column(JSON)  # Array of image URLs

    # Metadata
    historical_significance = Column(Text)
    tags = Column(JSON)  # Array of tags for search

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    region = relationship("Region", back_populates="pois")
    accessibility_info = relationship("AccessibilityInfo", back_populates="poi", uselist=False)
    special_deals = relationship("SpecialDeal", back_populates="poi")
    translations = relationship("TranslationSupport", back_populates="poi")

class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    language = Column(Enum(Language), default=Language.ENGLISH)
    interests = Column(JSON)  # Array of categories/interests
    travel_style = Column(String(50))  # budget, luxury, adventure, cultural
    accessibility_needs = Column(JSON)  # Array of accessibility requirements
    notification_preferences = Column(JSON)
    currency_preference = Column(String(3), default="EGP")

    # Relationships
    user = relationship("User", back_populates="preferences")

class TravelPlan(Base):
    __tablename__ = "travel_plans"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200))
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    destinations = Column(JSON)  # Array of region IDs
    planned_pois = Column(JSON)  # Array of POI IDs with scheduled times
    budget = Column(Float)
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="travel_plans")

class SavedItem(Base):
    __tablename__ = "saved_items"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    poi_id = Column(Integer, ForeignKey("pois.id"), nullable=False)
    save_type = Column(String(20))  # "favorite", "want_to_visit", "visited"
    notes = Column(Text)
    saved_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="saved_items")
    poi = relationship("POI")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    poi_id = Column(Integer, ForeignKey("pois.id"), nullable=False)
    recommendation_score = Column(Float)
    reason = Column(Text)
    recommendation_type = Column(String(50))  # "similar_pois", "nearby", "popular"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")
    poi = relationship("POI")

class UserRating(Base):
    __tablename__ = "user_ratings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    poi_id = Column(Integer, ForeignKey("pois.id"), nullable=False)
    rating = Column(Float, nullable=False)  # 1-5 scale
    review_text = Column(Text)
    visit_date = Column(DateTime(timezone=True))
    is_verified_visit = Column(Boolean, default=False)
    helpful_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="ratings")
    poi = relationship("POI")

class TranslationSupport(Base):
    __tablename__ = "translation_support"

    id = Column(Integer, primary_key=True)
    poi_id = Column(Integer, ForeignKey("pois.id"), nullable=False)
    field_name = Column(String(50), nullable=False)  # "name", "description", etc.
    language = Column(Enum(Language), nullable=False)
    translated_text = Column(Text, nullable=False)
    confidence_score = Column(Float)
    is_manual_translation = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    poi = relationship("POI", back_populates="translations")

class AccessibilityInfo(Base):
    __tablename__ = "accessibility_info"

    id = Column(Integer, primary_key=True)
    poi_id = Column(Integer, ForeignKey("pois.id"), nullable=False)
    accessibility_type = Column(Enum(AccessibilityType), nullable=False)
    is_available = Column(Boolean, nullable=False)
    description = Column(Text)
    description_arabic = Column(Text)
    specific_features = Column(JSON)  # Detailed accessibility features
    limitations = Column(Text)
    last_verified = Column(DateTime(timezone=True))

    # Relationships
    poi = relationship("POI", back_populates="accessibility_info")

class SpecialDeal(Base):
    __tablename__ = "special_deals"

    id = Column(Integer, primary_key=True)
    poi_id = Column(Integer, ForeignKey("pois.id"), nullable=False)
    title = Column(String(200), nullable=False)
    title_arabic = Column(String(200))
    description = Column(Text)
    description_arabic = Column(Text)
    discount_percentage = Column(Float)
    original_price = Column(Float)
    discounted_price = Column(Float)
    valid_from = Column(DateTime(timezone=True))
    valid_until = Column(DateTime(timezone=True))
    terms_conditions = Column(Text)
    terms_conditions_arabic = Column(Text)
    promo_code = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    poi = relationship("POI", back_populates="special_deals")

class UserAuth(Base):
    """Stores sensitive user authentication data (separate from profile)."""
    __tablename__ = "user_auth"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    profile = relationship("UserProfile", back_populates="auth", uselist=False)
    itineraries = relationship("Itinerary", back_populates="user_auth")


class UserProfile(Base):
    """The agentic profile data built by the AI (references user_auth)."""
    __tablename__ = "user_profiles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("user_auth.user_id"), primary_key=True)
    
    # Core Questionnaire Fields
    full_name = Column(String(100))
    home_country = Column(String(50))
    age_range = Column(Enum(AgeRangeType), name='age_range_type')
    typical_companions = Column(JSON)
    trips_per_year = Column(Integer)
    travel_style = Column(JSON, nullable=False) 
    accommodation_type_preference = Column(String(50))
    interest_scores = Column(JSON, nullable=False)
    itinerary_pace = Column(Enum(ItineraryPaceType), name='itinerary_pace_type', nullable=False)
    planning_style = Column(Enum(PlanningStyleType), name='planning_style_type', nullable=False)
    loved_trip_description = Column(Text)
    
    # Learned/Optional Fields
    mobility_preference = Column(String(50))
    comfort_level = Column(String(50))
    favorite_cuisines = Column(JSON)
    dietary_restrictions = Column(JSON)
    chronotype = Column(String(50))
    trip_budget_estimate = Column(Float)
    price_sensitivity = Column(String(50))
    accessibility_needs = Column(Text)
    personal_interests = Column(JSON)
    
    # Metadata
    allow_long_term_profile = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    auth = relationship("UserAuth", back_populates="profile")


class Itinerary(Base):
    """The trip header, grouping all activities."""
    __tablename__ = "itineraries"

    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_auth.user_id"), nullable=False)
    title = Column(String(200), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id"))
    status = Column(String(20), default="draft")
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    budget_allocated = Column(Float)
    agent_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user_auth = relationship("UserAuth", back_populates="itineraries")
    items = relationship("ItineraryItem", back_populates="itinerary")


class ItineraryItem(Base):
    """A single scheduled activity within a trip."""
    __tablename__ = "itinerary_items"

    id = Column(Integer, primary_key=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id"), nullable=False)
    poi_id = Column(Integer, ForeignKey("pois.id"))
    day_number = Column(Integer, nullable=False)
    sequence_order = Column(Integer, nullable=False)
    
    # Scheduling Details
    start_time = Column(String(50), nullable=False) # Representing TIME WITHOUT TIME ZONE
    end_time = Column(String(50))
    
    # Custom Event Details
    custom_title = Column(String(200))
    custom_description = Column(Text)
    custom_location = Column(String(500))
    
    # Tracking/Learning Fields
    is_booked = Column(Boolean, default=False)
    user_rating = Column(Float)
    agent_suggested = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    itinerary = relationship("Itinerary", back_populates="items")
    poi = relationship("POI")