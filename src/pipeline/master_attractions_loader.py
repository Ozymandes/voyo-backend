"""
Master Attractions Loader for VoyO
Loads curated attractions from master list for enrichment
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Iterator
import logging

# Add data directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "data"))

try:
    from master_attractions_clean import MASTER_ATTRACTIONS
except ImportError:
    # Fallback to sample version if available
    try:
        from master_attractions_sample import MASTER_ATTRACTIONS
    except ImportError:
        MASTER_ATTRACTIONS = {}

logger = logging.getLogger(__name__)


class MasterAttractionsLoader:
    """Loads and provides access to curated master attractions list"""

    def __init__(self):
        self.attractions = MASTER_ATTRACTIONS
        self._validate()

    def _validate(self):
        """Validate the master attractions list"""
        if not self.attractions:
            logger.warning("Master attractions list is empty or not loaded")

        # Count total attractions
        total = sum(len(pois) for pois in self.attractions.values())
        logger.info(f"Loaded {total} attractions across {len(self.attractions)} regions")

    def get_all_regions(self) -> List[str]:
        """Get list of all available regions"""
        return list(self.attractions.keys())

    def get_attractions_by_region(self, region: str) -> List[Dict[str, Any]]:
        """Get all attractions for a specific region"""
        return self.attractions.get(region, [])

    def get_all_attractions(self) -> Iterator[Dict[str, Any]]:
        """Iterate over all attractions across all regions"""
        for region, pois in self.attractions.items():
            for poi in pois:
                # Add region to POI data
                poi['region'] = region
                yield poi

    def get_attractions_by_importance(self, importance: str) -> List[Dict[str, Any]]:
        """Get all attractions with specific importance level"""
        results = []
        for region, pois in self.attractions.items():
            for poi in pois:
                if poi.get('importance') == importance:
                    poi['region'] = region
                    results.append(poi)
        return results

    def get_must_see_attractions(self) -> List[Dict[str, Any]]:
        """Get all Must-See and World Wonder attractions"""
        results = []
        for region, pois in self.attractions.items():
            for poi in pois:
                if poi.get('importance') in ['Must-See', 'World Wonder']:
                    poi['region'] = region
                    results.append(poi)
        return results

    def get_unesco_sites(self) -> List[Dict[str, Any]]:
        """Get all UNESCO World Heritage Sites"""
        results = []
        for region, pois in self.attractions.items():
            for poi in pois:
                if poi.get('UNESCO_site') == True:
                    poi['region'] = region
                    results.append(poi)
        return results

    def get_attractions_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all attractions in a specific category"""
        results = []
        for region, pois in self.attractions.items():
            for poi in pois:
                if poi.get('category') == category:
                    poi['region'] = region
                    results.append(poi)
        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the master attractions list"""
        stats = {
            'total_regions': len(self.attractions),
            'total_attractions': 0,
            'by_region': {},
            'by_importance': {
                'Must-See': 0,
                'World Wonder': 0,
                'Major': 0,
                'Minor': 0
            },
            'by_category': {},
            'unesco_sites': 0
        }

        for region, pois in self.attractions.items():
            count = len(pois)
            stats['total_attractions'] += count
            stats['by_region'][region] = count

            for poi in pois:
                # Count by importance
                importance = poi.get('importance', 'Unknown')
                if importance in stats['by_importance']:
                    stats['by_importance'][importance] += 1

                # Count by category
                category = poi.get('category', 'Unknown')
                stats['by_category'][category] = stats['by_category'].get(category, 0) + 1

                # Count UNESCO sites
                if poi.get('UNESCO_site') == True:
                    stats['unesco_sites'] += 1

        return stats

    def get_attraction_by_name(self, name: str) -> Dict[str, Any]:
        """Find attraction by name (fuzzy match)"""
        name_lower = name.lower()
        for region, pois in self.attractions.items():
            for poi in pois:
                if name_lower in poi['name'].lower():
                    poi['region'] = region
                    return poi
        return None

    def export_for_enrichment(self, region: str = None) -> List[Dict[str, Any]]:
        """
        Export attractions in format ready for enrichment pipeline
        Returns list with search queries and metadata
        """
        attractions = []

        if region:
            pois = self.get_attractions_by_region(region)
        else:
            pois = list(self.get_all_attractions())

        for poi in pois:
            export_data = {
                'name': poi['name'],
                'name_arabic': poi.get('name_arabic', ''),
                'region': poi.get('region', region),
                'category': poi.get('category', 'Unknown'),
                'importance': poi.get('importance', 'Unknown'),
                'search_queries': poi.get('search_queries', [poi['name']]),
                'description': poi.get('description', ''),
                'expected_rating': poi.get('expected_rating', 0.0),
                'ticket_price': poi.get('ticket_price'),
                'unesco_site': poi.get('UNESCO_site', False)
            }
            attractions.append(export_data)

        return attractions


# Convenience functions
def load_master_attractions() -> MasterAttractionsLoader:
    """Load and return master attractions loader instance"""
    return MasterAttractionsLoader()


def get_regions() -> List[str]:
    """Get list of all available regions"""
    loader = MasterAttractionsLoader()
    return loader.get_all_regions()


def get_all_attractions() -> List[Dict[str, Any]]:
    """Get all attractions as a list"""
    loader = MasterAttractionsLoader()
    return list(loader.get_all_attractions())


if __name__ == "__main__":
    # Test the loader
    loader = MasterAttractionsLoader()

    print("\n" + "="*70)
    print("MASTER ATTRACTIONS LOADER - TEST")
    print("="*70)

    # Print statistics
    stats = loader.get_statistics()
    print(f"\nRegions: {stats['total_regions']}")
    print(f"Total Attractions: {stats['total_attractions']}")
    print(f"UNESCO Sites: {stats['unesco_sites']}")

    print("\nBy Region:")
    for region, count in stats['by_region'].items():
        print(f"  {region}: {count}")

    print("\nBy Importance:")
    for importance, count in stats['by_importance'].items():
        if count > 0:
            print(f"  {importance}: {count}")

    print("\nBy Category:")
    for category, count in sorted(stats['by_category'].items()):
        print(f"  {category}: {count}")

    # Show sample Must-See attractions
    print("\nSample Must-See Attractions:")
    must_see = loader.get_must_see_attractions()
    for poi in must_see[:5]:
        print(f"  - {poi['name']} ({poi.get('region')})")

    print("\n" + "="*70)
    print("Loader test completed successfully!")
    print("="*70)
