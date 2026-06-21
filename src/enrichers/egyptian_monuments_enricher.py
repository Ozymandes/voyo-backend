"""
VoyO Egyptian Monuments Scraper - Simplified
Uses Playwright sync API for easier usage
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class EgyptianMonumentsScraper:
    """Scrapes official Egyptian government monument data using Playwright sync"""

    def __init__(self):
        self.base_url = "https://egymonuments.gov.eg/en/monuments"
        self.playwright = None
        self.browser = None
        self.page = None
        self._initialized = False

    def _initialize_browser(self):
        """Initialize Playwright browser (synchronous)"""
        if self._initialized:
            return True

        try:
            from playwright.sync_api import sync_playwright

            self.playwright = sync_playwright().start()

            # Launch browser
            self.browser = self.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )

            self.page = self.browser.new_page()
            self._initialized = True

            logger.info("Browser initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize browser: {str(e)}")
            return False

    def close(self):
        """Close browser"""
        if self.browser:
            try:
                self.browser.close()
            except:
                pass
        if self.playwright:
            try:
                self.playwright.stop()
            except:
                pass
        self._initialized = False
        logger.info("Browser closed")

    def search_monument(self, poi_name: str) -> Optional[Dict[str, Any]]:
        """Search for a monument on egymonuments.gov.eg"""

        if not self._initialize_browser():
            return None

        try:
            logger.info(f"Searching egymonuments.gov.eg for: {poi_name}")

            # Navigate to monuments page
            self.page.goto(self.base_url, wait_until='networkidle', timeout=30000)
            self.page.wait_for_timeout(2000)  # Wait for JS to load

            # Get page content and analyze
            page_content = self.page.content()

            # Check if monument name appears in page
            if poi_name.lower() in page_content.lower():
                logger.info(f"Found mention of {poi_name} on page")

                # Try to extract pricing/hours data
                return self._extract_data_from_page(poi_name)
            else:
                logger.warning(f"{poi_name} not found on page")
                return None

        except Exception as e:
            logger.error(f"Error searching for {poi_name}: {str(e)}")
            return None

    def _extract_data_from_page(self, poi_name: str) -> Optional[Dict[str, Any]]:
        """Extract data from current page"""

        try:
            data = {
                'ticket_price_tourist': None,
                'ticket_price_egyptian': None,
                'opening_hours': None,
                'description': None,
                'source': 'egymonuments.gov.eg',
                'scraped_at': datetime.now().isoformat()
            }

            # Get all text content
            page_text = self.page.inner_text('body')

            # Extract prices using regex
            import re

            # Look for EGP prices
            price_pattern = r'(\d+)\s*(?:EGP|Egp|egyptian pounds?|pounds?)'
            prices = re.findall(price_pattern, page_text, re.IGNORECASE)

            if prices:
                # Convert to integers and sort
                price_values = sorted([int(p) for p in prices if p.isdigit()])

                if len(price_values) >= 2:
                    # Assume lowest is Egyptian, highest is tourist
                    data['ticket_price_egyptian'] = price_values[0]
                    data['ticket_price_tourist'] = price_values[-1]
                    logger.info(f"Found prices: EGP {price_values[0]} (Egyptian), EGP {price_values[-1]} (Tourist)")
                elif len(price_values) == 1:
                    data['ticket_price_tourist'] = price_values[0]
                    logger.info(f"Found price: EGP {price_values[0]}")

            # Look for opening hours
            hour_patterns = [
                r'(?:open|opens?)\s*(?:at|from)?\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)',
                r'(?:close|closes?)\s*(?:at)?\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)',
                r'(\d{1,2}:\d{2}\s*(?:am|pm)?)\s*-\s*(\d{1,2}:\d{2}\s*(?:am|pm)?)'
            ]

            for pattern in hour_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                if matches:
                    # Extract surrounding context
                    for match in matches:
                        idx = page_text.lower().find(match[0] if isinstance(match, tuple) else match)
                        if idx > 0:
                            context = page_text[max(0, idx-50):idx+100]
                            if 'hour' in context.lower() or 'open' in context.lower() or 'close' in context.lower():
                                data['opening_hours'] = context.strip()
                                logger.info(f"Found hours info")
                                break
                    if data['opening_hours']:
                        break

            return data if any([data['ticket_price_tourist'], data['opening_hours']]) else None

        except Exception as e:
            logger.error(f"Error extracting data: {str(e)}")
            return None

    def enrich_poi(self, poi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main enrichment method"""
        name = poi_data.get('name')
        logger.info(f"Enriching {name} from Egyptian Monuments...")

        try:
            monument_data = self.search_monument(name)

            if monument_data:
                enriched = poi_data.copy()

                if monument_data.get('ticket_price_tourist'):
                    enriched['ticket_price_tourist'] = monument_data['ticket_price_tourist']
                if monument_data.get('ticket_price_egyptian'):
                    enriched['ticket_price_egyptian'] = monument_data['ticket_price_egyptian']
                if monument_data.get('opening_hours'):
                    enriched['opening_hours_monuments'] = monument_data['opening_hours']

                enriched['monuments_scraped'] = True
                enriched['monuments_scraped_at'] = datetime.now().isoformat()

                logger.info(f"Successfully enriched {name}")
                return enriched
            else:
                logger.warning(f"No data found for {name}")
                return poi_data

        except Exception as e:
            logger.error(f"Error enriching {name}: {str(e)}")
            return poi_data


# Test function
def test_monuments_scraper():
    """Test the monuments scraper"""

    scraper = EgyptianMonumentsScraper()

    try:
        # Test POIs
        test_pois = [
            {'name': 'Pyramids of Giza', 'category': 'Historical'},
            {'name': 'Egyptian Museum', 'category': 'Museum'},
            {'name': 'Khan el-Khalili', 'category': 'Historical'}
        ]

        print("="*70)
        print("TESTING EGYPTIAN MONUMENTS SCRAPER")
        print("="*70)

        for i, poi in enumerate(test_pois, 1):
            print(f"\n[{i}/{len(test_pois)}] Testing: {poi['name']}")
            print("-"*70)

            result = scraper.enrich_poi(poi)

            if result.get('monuments_scraped'):
                print("SUCCESS! Found data:")
                if result.get('ticket_price_tourist'):
                    print(f"  Tourist Price: {result['ticket_price_tourist']} EGP")
                if result.get('ticket_price_egyptian'):
                    print(f"  Egyptian Price: {result['ticket_price_egyptian']} EGP")
                if result.get('opening_hours_monuments'):
                    hours = result['opening_hours_monuments']
                    print(f"  Hours: {hours[:100]}..." if len(hours) > 100 else f"  Hours: {hours}")
            else:
                print("No data found")

        print("\n" + "="*70)
        print("TEST COMPLETE")
        print("="*70)

    finally:
        print("\nClosing browser...")
        scraper.close()
        print("Done!")


if __name__ == "__main__":
    test_monuments_scraper()
