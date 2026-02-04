"""
Data Processing and Cleaning Pipeline
Processes and validates scraped POI data before database insertion
"""

import logging
import re
import hashlib
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

from scrapers.base_scraper import POIData, POICategory

logger = logging.getLogger(__name__)

@dataclass
class ProcessingStats:
    """Statistics for data processing"""
    total_processed: int = 0
    valid_pois: int = 0
    duplicates_removed: int = 0
    invalid_coordinates: int = 0
    missing_required_fields: int = 0
    categorization_updated: int = 0
    enhanced_with_images: int = 0
    validation_errors: List[str] = None

    def __post_init__(self):
        if self.validation_errors is None:
            self.validation_errors = []

class DataProcessor:
    """Processes and validates scraped POI data"""

    def __init__(self):
        self.processed_hashes: Set[str] = set()
        self.stats = ProcessingStats()
        self.region_keywords = self._load_region_keywords()

    def _load_region_keywords(self) -> Dict[str, List[str]]:
        """Load region-specific keywords for better categorization"""
        return {
            "Cairo": [
                "egyptian museum", "khan el-khalili", "citadel", "coptic cairo",
                "islamic cairo", "al-azhar", "sultan hassan", "al-muizz",
                "cairo tower", "zamalek", "giza plateau", "nile"
            ],
            "Giza": [
                "pyramid", "sphinx", "memphis", "saqqara", "dashur",
                "great pyramid", "khufu", "khafre", "menkaure",
                "valley temple", "mortuary temple", "solar boat"
            ],
            "Alexandria": [
                "bibliotheca", "montazah", "corniche", "pompey pillar",
                "catacombs", "fort qaitbay", "stanley bridge",
                "ramla station", "sidi gaber", "kafr abdu"
            ],
            "Luxor": [
                "karnak", "luxor temple", "valley of kings", "hatshepsut",
                "medinet habu", "colossi of memnon", "deir el-bahri",
                "deir el-medina", "tomb workers", "ancient thebes"
            ],
            "Aswan": [
                "philae", "abu simbel", "nubian", "elephantine island",
                "high dam", "unfinished obelisk", "kitchener island",
                "sehel island", "nubian museum", "kom ombo", "edfu"
            ],
            "Hurghada": [
                "marina", "old town", "new marina", "sahl hasheesh",
                "makadi bay", "el gouna", "giftun island", "soma bay",
                "red sea", "diving", "snorkeling", "coral reef"
            ],
            "Marsa Alam": [
                "port ghalib", "wadi el gemal", "sataya", "abu dabbab",
                "sharm el luli", "wadi el gamal", "wadi samlah",
                "red sea", "marine park", "dolphin", "sea turtle"
            ],
            "Sinai": [
                "mount sinai", "saint catherine", "sharm el sheikh",
                "dahab", "nuweiba", "taba", "ras muhammad",
                "colored canyon", "blue hole", "monastery"
            ]
        }

    def process_pois(self, pois: List[POIData], region_name: str) -> Tuple[List[POIData], ProcessingStats]:
        """Process a list of POIs and return cleaned data with statistics"""
        logger.info(f"Starting data processing for {len(pois)} POIs from {region_name}")

        processed_pois = []
        self.stats = ProcessingStats()
        self.processed_hashes.clear()

        for poi in pois:
            self.stats.total_processed += 1

            try:
                # Skip duplicates
                poi_hash = self._generate_poi_hash(poi)
                if poi_hash in self.processed_hashes:
                    self.stats.duplicates_removed += 1
                    continue

                self.processed_hashes.add(poi_hash)

                # Validate required fields
                if not self._validate_required_fields(poi):
                    self.stats.missing_required_fields += 1
                    continue

                # Validate coordinates
                if not self._validate_coordinates(poi):
                    self.stats.invalid_coordinates += 1
                    continue

                # Clean and enhance data
                cleaned_poi = self._clean_poi_data(poi, region_name)
                if not cleaned_poi:
                    continue

                # Enhance categorization
                if self._enhance_categorization(cleaned_poi, region_name):
                    self.stats.categorization_updated += 1

                # Add region-specific enhancements
                self._add_region_enhancements(cleaned_poi, region_name)

                # Validate final POI
                if self._validate_final_poi(cleaned_poi):
                    processed_pois.append(cleaned_poi)
                    self.stats.valid_pois += 1
                else:
                    self.stats.validation_errors.append(f"Failed validation: {cleaned_poi.name}")

            except Exception as e:
                logger.error(f"Error processing POI {poi.name}: {str(e)}")
                self.stats.validation_errors.append(f"Processing error: {poi.name} - {str(e)}")

        logger.info(f"Processing complete. Valid POIs: {self.stats.valid_pois}/{self.stats.total_processed}")
        return processed_pois, self.stats

    def _generate_poi_hash(self, poi: POIData) -> str:
        """Generate unique hash for POI to identify duplicates"""
        hash_data = f"{poi.name.lower().strip()}|{poi.latitude}|{poi.longitude}"
        return hashlib.md5(hash_data.encode()).hexdigest()

    def _validate_required_fields(self, poi: POIData) -> bool:
        """Validate that required fields are present"""
        if not poi or not poi.name or not poi.name.strip():
            return False

        # Check if we have coordinates
        if poi.latitude is None or poi.longitude is None:
            return False

        return True

    def _validate_coordinates(self, poi: POIData) -> bool:
        """Validate coordinates are within reasonable bounds for Egypt"""
        lat, lon = poi.latitude, poi.longitude

        # Egypt approximate bounds
        if not (22.0 <= lat <= 31.5 and 24.0 <= lon <= 36.0):
            logger.warning(f"Coordinates outside Egypt bounds: {lat}, {lon} for {poi.name}")
            return False

        return True

    def _clean_poi_data(self, poi: POIData, region_name: str) -> Optional[POIData]:
        """Clean and standardize POI data"""
        try:
            # Clean name
            poi.name = self._clean_text(poi.name)
            if not poi.name:
                return None

            # Clean descriptions
            if poi.description:
                poi.description = self._clean_text(poi.description)

            if poi.description_arabic:
                poi.description_arabic = self._clean_text(poi.description_arabic)

            # Clean address
            if poi.address:
                poi.address = self._clean_text(poi.address)
                # Ensure city is set
                if not poi.city:
                    poi.city = region_name

            # Clean phone number
            if poi.phone_number:
                poi.phone_number = self._clean_phone_number(poi.phone_number)

            # Clean website URL
            if poi.website_url:
                poi.website_url = self._clean_url(poi.website_url)

            # Clean email
            if poi.email_address:
                poi.email_address = self._clean_email(poi.email_address)

            # Ensure category
            if not poi.category:
                poi.category = POICategory.SERVICES

            # Clean tags
            if poi.tags:
                poi.tags = [self._clean_text(tag) for tag in poi.tags if tag]
                poi.tags = [tag for tag in poi.tags if tag]

            # Set defaults
            if not poi.currency:
                poi.currency = "EGP"

            if not poi.source:
                poi.source = "Processed"

            return poi

        except Exception as e:
            logger.error(f"Error cleaning POI data for {poi.name}: {str(e)}")
            return None

    def _clean_text(self, text: str) -> str:
        """Clean and standardize text"""
        if not text:
            return ""

        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())

        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s\-.,;:()&@#%/]', '', text)

        return text.strip()

    def _clean_phone_number(self, phone: str) -> str:
        """Clean and standardize phone number"""
        if not phone:
            return ""

        # Remove all non-digit characters except +
        phone = re.sub(r'[^\d+]', '', phone)

        # Ensure Egyptian country code if it looks like a local number
        if phone.startswith('0') and len(phone) == 10:
            phone = '+2' + phone

        return phone

    def _clean_url(self, url: str) -> str:
        """Clean and validate URL"""
        if not url:
            return ""

        # Basic URL cleaning
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        return url

    def _clean_email(self, email: str) -> str:
        """Clean email address"""
        if not email:
            return ""

        email = email.strip().lower()

        # Basic email validation
        if '@' not in email:
            return ""

        return email

    def _enhance_categorization(self, poi: POIData, region_name: str) -> bool:
        """Enhance POI categorization based on region and content"""
        original_category = poi.category
        name_lower = poi.name.lower()
        description_lower = (poi.description or "").lower()
        tags_lower = [tag.lower() for tag in (poi.tags or [])]

        # Region-specific categorization
        region_keywords = self.region_keywords.get(region_name, [])
        for keyword in region_keywords:
            if keyword in name_lower or keyword in description_lower:
                # Found region-specific keyword
                if "museum" in keyword or "pyramid" in keyword or "temple" in keyword:
                    poi.category = POICategory.HISTORICAL
                elif "mall" in keyword or "market" in keyword:
                    poi.category = POICategory.SHOPPING
                elif "park" in keyword or "beach" in keyword:
                    poi.category = POICategory.NATURAL
                break

        # Content-based enhancement
        if any(word in name_lower or word in description_lower for word in
               ['mosque', 'church', 'monastery', 'temple', 'religious']):
            poi.category = POICategory.RELIGIOUS

        return poi.category != original_category

    def _add_region_enhancements(self, poi: POIData, region_name: str):
        """Add region-specific enhancements to POI"""
        # Add regional tags
        region_tags = {
            "Cairo": ["capital", "metropolitan", "cosmopolitan"],
            "Giza": ["pyramids", "ancient egypt", "memphis"],
            "Alexandria": ["mediterranean", "coastal", "greek"],
            "Luxor": ["ancient thebes", "pharaohs", "temples"],
            "Aswan": ["nubian", "upper egypt", "high dam"],
            "Hurghada": ["red sea", "resort", "diving"],
            "Marsa Alam": ["red sea", "marine", "ecotourism"],
            "Sinai": ["mountain", "peninsula", "bedouin"]
        }

        if region_name in region_tags:
            if not poi.tags:
                poi.tags = []
            poi.tags.extend(region_tags[region_name])

        # Set city if not set
        if not poi.city:
            poi.city = region_name

        # Add regional historical significance for historical sites
        if poi.category == POICategory.HISTORICAL and not poi.historical_significance:
            historical_contexts = {
                "Cairo": "Islamic and Coptic heritage in Egypt's capital",
                "Giza": "Ancient Egyptian royal necropolis and pyramids",
                "Alexandria": "Greco-Roman and Ptolemaic history on the Mediterranean",
                "Luxor": "Capital of ancient Egypt during the New Kingdom",
                "Aswan": "Southern frontier and Nubian culture",
                "Sinai": "Biblical sites and desert monasticism"
            }

            if region_name in historical_contexts:
                poi.historical_significance = historical_contexts[region_name]

    def _validate_final_poi(self, poi: POIData) -> bool:
        """Final validation of processed POI"""
        # Check all critical fields
        if not poi.name or not poi.name.strip():
            return False

        if not poi.category:
            return False

        if poi.latitude is None or poi.longitude is None:
            return False

        # Check coordinate ranges
        if not (-90 <= poi.latitude <= 90 and -180 <= poi.longitude <= 180):
            return False

        return True

    def generate_processing_report(self) -> Dict[str, Any]:
        """Generate detailed processing report"""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "statistics": asdict(self.stats),
            "success_rate": (self.stats.valid_pois / max(1, self.stats.total_processed)) * 100,
            "duplicate_rate": (self.stats.duplicates_removed / max(1, self.stats.total_processed)) * 100,
            "quality_score": min(100, (self.stats.valid_pois / max(1, self.stats.total_processed)) * 100)
        }

    def detect_potential_duplicates(self, pois: List[POIData], similarity_threshold: float = 0.8) -> List[Tuple[int, int, float]]:
        """Detect potential duplicates based on name and location similarity"""
        duplicates = []

        for i, poi1 in enumerate(pois):
            for j, poi2 in enumerate(pois[i+1:], i+1):
                similarity = self._calculate_similarity(poi1, poi2)

                if similarity >= similarity_threshold:
                    duplicates.append((i, j, similarity))

        return duplicates

    def _calculate_similarity(self, poi1: POIData, poi2: POIData) -> float:
        """Calculate similarity score between two POIs"""
        # Name similarity (40% weight)
        name_similarity = self._string_similarity(poi1.name.lower(), poi2.name.lower()) * 0.4

        # Location similarity (40% weight)
        if poi1.latitude and poi1.longitude and poi2.latitude and poi2.longitude:
            # Simple distance-based similarity
            distance = ((poi1.latitude - poi2.latitude)**2 + (poi1.longitude - poi2.longitude)**2)**0.5
            location_similarity = max(0, 1 - distance) * 0.4
        else:
            location_similarity = 0

        # Category similarity (20% weight)
        category_similarity = 1.0 if poi1.category == poi2.category else 0.0

        return name_similarity + location_similarity + category_similarity

    def _string_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity using Levenshtein distance approximation"""
        if not str1 or not str2:
            return 0.0

        # Simple character overlap ratio
        chars1 = set(str1)
        chars2 = set(str2)
        overlap = len(chars1 & chars2)
        union = len(chars1 | chars2)

        return overlap / union if union > 0 else 0.0