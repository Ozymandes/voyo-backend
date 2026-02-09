"""
Dead Letter Queue for Failed POIs
Stores and manages failed POIs for manual review and retry
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class DeadLetterQueue:
    """Store failed POIs for manual review/retry"""

    def __init__(self, dlq_path: str = "data/failed_pois.json"):
        """Initialize DLQ with file path"""
        self.dlq_path = Path(dlq_path)
        self.failed_pois = self._load()

    def _load(self) -> List[Dict]:
        """Load failed POIs from disk"""
        if self.dlq_path.exists():
            try:
                with open(self.dlq_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading DLQ: {e}")
                return []
        return []

    def _save(self):
        """Save failed POIs to disk"""
        try:
            self.dlq_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.dlq_path, 'w', encoding='utf-8') as f:
                json.dump(self.failed_pois, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving DLQ: {e}")

    def add(self, attraction: Dict, error: str, stage: str = "unknown"):
        """Add failed POI to queue"""
        failed_poi = {
            'name': attraction.get('name', 'Unknown'),
            'region': attraction.get('region', 'Unknown'),
            'error': error,
            'stage': stage,  # 'google_places', 'wikipedia', 'database'
            'failed_at': datetime.now().isoformat(),
            'retry_count': 0,
            'attraction_data': attraction
        }
        self.failed_pois.append(failed_poi)
        self._save()
        logger.warning(f"Added to DLQ: {failed_poi['name']} ({stage}): {error}")

    def get_all(self) -> List[Dict]:
        """Get all failed POIs"""
        return self.failed_pois

    def get_by_stage(self, stage: str) -> List[Dict]:
        """Get failed POIs by stage"""
        return [poi for poi in self.failed_pois if poi['stage'] == stage]

    def get_by_region(self, region: str) -> List[Dict]:
        """Get failed POIs by region"""
        return [poi for poi in self.failed_pois if poi['region'] == region]

    def mark_retried(self, index: int):
        """Mark POI as retried"""
        if 0 <= index < len(self.failed_pois):
            self.failed_pois[index]['retry_count'] += 1
            self.failed_pois[index]['last_retry'] = datetime.now().isoformat()
            self._save()

    def remove(self, index: int):
        """Remove POI from queue (after successful retry)"""
        if 0 <= index < len(self.failed_pois):
            removed = self.failed_pois.pop(index)
            self._save()
            logger.info(f"Removed from DLQ: {removed['name']}")

    def clear_all(self):
        """Clear all failed POIs"""
        count = len(self.failed_pois)
        self.failed_pois = []
        self._save()
        logger.info(f"Cleared {count} POIs from DLQ")

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of failed POIs"""
        stages = {}
        for poi in self.failed_pois:
            stage = poi['stage']
            stages[stage] = stages.get(stage, 0) + 1

        return {
            'total_failed': len(self.failed_pois),
            'by_stage': stages,
            'never_retried': sum(1 for poi in self.failed_pois if poi['retry_count'] == 0),
            'retried_multiple': sum(1 for poi in self.failed_pois if poi['retry_count'] > 1)
        }

    def export_report(self, report_path: str = "data/failed_pois_report.txt"):
        """Export human-readable report"""
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("="*70 + "\n")
                f.write("VOYO DEAD LETTER QUEUE REPORT\n")
                f.write("="*70 + "\n\n")

                summary = self.get_summary()
                f.write(f"Total Failed: {summary['total_failed']}\n")
                f.write(f"Never Retried: {summary['never_retried']}\n")
                f.write(f"Retried Multiple: {summary['retried_multiple']}\n\n")

                f.write("By Stage:\n")
                for stage, count in summary['by_stage'].items():
                    f.write(f"  - {stage}: {count}\n")

                f.write("\n" + "="*70 + "\n")
                f.write("DETAILS\n")
                f.write("="*70 + "\n\n")

                for i, poi in enumerate(self.failed_pois, 1):
                    f.write(f"{i}. {poi['name']} ({poi['region']})\n")
                    f.write(f"   Stage: {poi['stage']}\n")
                    f.write(f"   Error: {poi['error']}\n")
                    f.write(f"   Failed: {poi['failed_at']}\n")
                    f.write(f"   Retries: {poi['retry_count']}\n\n")

            logger.info(f"Exported DLQ report to {report_path}")
        except Exception as e:
            logger.error(f"Error exporting report: {e}")
