"""
VoyO Wikipedia Enricher with LLM Integration
Extracts historical and cultural information from Wikipedia
"""

import os
import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class WikipediaScraper:
    """Scrapes Wikipedia pages for tourist attractions"""

    def __init__(self):
        self.base_url = "https://en.wikipedia.org/api/rest_v1"
        self.arabic_base_url = "https://ar.wikipedia.org/api/rest_v1"
        # Add user agent to avoid 403 errors
        self.headers = {
            'User-Agent': 'VoyO-Tourism-App/1.0 (Educational purpose; contact: voyo-app@example.com)'
        }

    def search_article(self, poi_name: str, region: str = "Egypt") -> Optional[str]:
        """
        Search for Wikipedia article about a POI

        Returns: Article title if found, None otherwise
        """
        # Try direct lookup first
        search_url = f"{self.base_url}/page/summary/{poi_name}"

        try:
            response = requests.get(search_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Verify it's about Egypt/the attraction
                extract = data.get('extract', '')
                if extract and self._is_egypt_related(extract):
                    return data.get('title')

            # If direct lookup fails, try search API
            search_api_url = "https://en.wikipedia.org/w/api.php"
            search_params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': f"{poi_name} {region}",
                'srlimit': 5
            }

            search_response = requests.get(search_api_url, params=search_params, headers=self.headers, timeout=10)
            if search_response.status_code == 200:
                search_data = search_response.json()
                results = search_data.get('query', {}).get('search', [])

                for result in results:
                    title = result.get('title')
                    # Try to get this article's summary
                    summary_url = f"{self.base_url}/page/summary/{title}"
                    summary_resp = requests.get(summary_url, headers=self.headers, timeout=10)

                    if summary_resp.status_code == 200:
                        summary_data = summary_resp.json()
                        extract = summary_data.get('extract', '')
                        if extract and self._is_egypt_related(extract):
                            return title

            return None

        except Exception as e:
            logger.error(f"Error searching Wikipedia for {poi_name}: {str(e)}")
            return None

    def get_article_content(self, title: str, language: str = "en") -> Optional[Dict[str, Any]]:
        """
        Get full article content including sections

        Returns: Dictionary with article text, sections, etc.
        """
        base = self.arabic_base_url if language == "ar" else self.base_url

        # Get article summary
        summary_url = f"{base}/page/summary/{title}"
        # Get detailed content (mobile format is cleaner)
        content_url = f"https://{language}.wikipedia.org/w/api.php"

        try:
            # Get summary
            summary_response = requests.get(summary_url, headers=self.headers, timeout=10)
            summary_data = summary_response.json() if summary_response.status_code == 200 else {}

            # Get full content with sections
            content_params = {
                'action': 'query',
                'format': 'json',
                'prop': 'extracts|pageprops',
                'exintro': True,
                'explaintext': True,
                'titles': title,
                'ppprop': 'wikibase_item'
            }

            content_response = requests.get(content_url, params=content_params, headers=self.headers, timeout=10)

            if content_response.status_code == 200:
                content_data = content_response.json()
                pages = content_data.get('query', {}).get('pages', {})

                # Get the first page (should be our article)
                page_id = next(iter(pages.keys()))
                page_data = pages[page_id]

                if page_id != '-1':  # -1 means page not found
                    return {
                        'title': page_data.get('title', title),
                        'extract': page_data.get('extract', ''),
                        'summary': summary_data.get('extract', ''),
                        'wikibase_id': page_data.get('pageprops', {}).get('wikibase_item'),
                        'language': language
                    }

            return None

        except Exception as e:
            logger.error(f"Error fetching Wikipedia article {title}: {str(e)}")
            return None

    def get_arabic_article(self, english_title: str) -> Optional[Dict[str, Any]]:
        """Get Arabic version of Wikipedia article"""
        # Try to get Arabic version by searching with the same title
        return self.get_article_content(english_title, language="ar")

    def _is_egypt_related(self, text: str) -> bool:
        """Check if article is about Egypt/Egyptian attractions"""
        egypt_keywords = ['egypt', 'egyptian', 'cairo', 'giza', 'luxor', 'aswan', 'alexandria']
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in egypt_keywords)


class LLMContentExtractor:
    """Uses LLM to extract structured information from Wikipedia text"""

    def __init__(self):
        # For now, we'll use a rule-based approach
        # You can integrate OpenAI/Anthropic API later
        pass

    def extract_historical_significance(self, article_text: str, poi_name: str) -> str:
        """
        Extract historical significance from Wikipedia article

        This is a rule-based version. For better results, integrate with:
        - OpenAI GPT-4
        - Anthropic Claude
        - Or open-source LLM (LLaMA, Mistral)
        """
        if not article_text:
            return ""

        # Rule-based extraction (first 3 sentences usually contain key info)
        sentences = article_text.split('. ')

        # Take first 3 sentences, up to 500 chars
        significance = '. '.join(sentences[:3])
        if len(significance) > 500:
            significance = significance[:497] + "..."

        return significance

    def generate_arabic_translation(self, english_text: str) -> str:
        """
        Generate Arabic translation

        Options:
        1. Google Translate API
        2. OpenAI GPT-4 (better context)
        3. Anthropic Claude
        4. Local model (for privacy/cost)

        For now: Return placeholder (you'll implement actual translation)
        """
        # TODO: Integrate translation API
        return ""  # Placeholder

    def extract_visit_duration(self, article_text: str) -> Optional[int]:
        """
        Extract recommended visit duration from text

        Returns: Duration in minutes (integer)
        """
        # Look for time-related keywords
        keywords = {
            'hour': 60,
            'hours': 60,
            'minute': 1,
            'minutes': 1,
            'half day': 240,
            'full day': 480
        }

        text_lower = article_text.lower()

        for keyword, minutes in keywords.items():
            if keyword in text_lower:
                # Try to extract number before the keyword
                words = text_lower.split()
                for i, word in enumerate(words):
                    if keyword in word:
                        try:
                            if i > 0:
                                num = float(words[i-1])
                                return int(num * minutes)
                        except:
                            return minutes

        # Default: 2 hours for historical sites
        return 120

    def extract_best_visit_times(self, article_text: str) -> Dict[str, str]:
        """
        Extract best times to visit from article

        Returns: {'season': '...', 'time_of_day': '...'}
        """
        text_lower = article_text.lower()

        # Extract seasonal information
        seasonal_keywords = {
            'winter': 'Winter (October - April)',
            'summer': 'Summer (May - September)',
            'spring': 'Spring (March - May)',
            'autumn': 'Autumn (September - November)'
        }

        best_season = "Year-round"
        for keyword, recommendation in seasonal_keywords.items():
            if keyword in text_lower:
                best_season = recommendation
                break

        # Extract time of day
        time_keywords = {
            'morning': 'Morning (8 AM - 12 PM)',
            'evening': 'Evening (4 PM - 7 PM)',
            'sunset': 'Sunset',
            'sunrise': 'Sunrise',
            'night': 'Evening/Night'
        }

        best_time = "Any time"
        for keyword, recommendation in time_keywords.items():
            if keyword in text_lower:
                best_time = recommendation
                break

        return {
            'season': best_season,
            'time_of_day': best_time
        }

    def extract_tags(self, article_text: str, poi_name: str, category: str) -> list:
        """
        Extract relevant tags for search and filtering

        Returns: List of tag strings
        """
        tags = [category.lower()]

        # Common Egyptian attraction tags
        common_tags = [
            'historical', 'ancient', 'islamic', 'coptic', 'unesco',
            'museum', 'mosque', 'church', 'temple', 'pyramid',
            'market', 'bazaar', 'fortress', 'citadel', 'palace',
            'cultural', 'archaeological', 'monument', 'landmark',
            'family-friendly', 'photography', 'architecture'
        ]

        text_lower = article_text.lower()

        for tag in common_tags:
            if tag in text_lower or tag.replace('-', ' ') in text_lower:
                if tag not in tags:
                    tags.append(tag)

        return tags[:10]  # Limit to 10 tags


class WikipediaEnricher:
    """Main Wikipedia enrichment orchestrator"""

    def __init__(self):
        self.scraper = WikipediaScraper()
        self.extractor = LLMContentExtractor()

    def enrich_poi(self, poi_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a POI with Wikipedia data

        Args:
            poi_data: Existing POI data from pipeline

        Returns:
            Enriched POI data with Wikipedia fields added
        """
        name = poi_data.get('name')
        region = poi_data.get('region', 'Egypt')

        logger.info(f"Enriching {name} from Wikipedia...")

        # Search for Wikipedia article
        article_title = self.scraper.search_article(name, region)

        if not article_title:
            logger.warning(f"No Wikipedia article found for {name}")
            return poi_data

        logger.info(f"Found Wikipedia article: {article_title}")

        # Get English article content
        article = self.scraper.get_article_content(article_title, language="en")

        if not article:
            logger.warning(f"Could not fetch article content for {article_title}")
            return poi_data

        extract_text = article.get('extract', '')
        summary_text = article.get('summary', '')
        full_text = extract_text or summary_text

        # Extract structured information using LLM
        enriched = poi_data.copy()

        # Historical significance (English)
        enriched['historical_significance'] = self.extractor.extract_historical_significance(
            full_text, name
        )

        # Try to get Arabic article
        arabic_article = self.scraper.get_arabic_article(article_title)
        if arabic_article:
            arabic_text = arabic_article.get('extract', '')
            # Historical significance (Arabic)
            enriched['historical_significance_arabic'] = self.extractor.extract_historical_significance(
                arabic_text, name
            )
        else:
            enriched['historical_significance_arabic'] = ""

        # Visit duration
        enriched['average_visit_duration'] = self.extractor.extract_visit_duration(full_text)

        # Best visit times
        enriched['best_visit_times'] = self.extractor.extract_best_visit_times(full_text)

        # Tags
        enriched['tags'] = self.extractor.extract_tags(
            full_text, name, poi_data.get('category', 'attraction')
        )

        # Add metadata
        enriched['data_sources'] = poi_data.get('data_sources', []) + ['wikipedia']
        enriched['wikipedia_enriched'] = True
        enriched['wikipedia_enriched_at'] = datetime.now().isoformat()

        logger.info(f"Successfully enriched {name} with Wikipedia data")
        logger.info(f"  - Historical significance: {len(enriched['historical_significance'])} chars")
        logger.info(f"  - Visit duration: {enriched['average_visit_duration']} minutes")
        logger.info(f"  - Tags: {enriched['tags']}")

        return enriched


# Test function
def test_wikipedia_enricher():
    """Test the Wikipedia enricher"""
    import json

    enricher = WikipediaEnricher()

    test_poi = {
        'name': 'Khan el-Khalili',
        'region': 'Cairo',
        'category': 'Historical',
        'description': 'Famous historic souk in Islamic Cairo'
    }

    print("="*70)
    print("TESTING WIKIPEDIA ENRICHER")
    print("="*70)
    print(f"\nEnriching: {test_poi['name']}\n")

    enriched = enricher.enrich_poi(test_poi)

    print("\nENRICHED DATA:")
    print(json.dumps(enriched, indent=2))
    print("\n" + "="*70)


if __name__ == "__main__":
    test_wikipedia_enricher()
