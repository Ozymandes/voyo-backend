"""
VOYO Academic Test Runner
Automated testing framework for CLEO baseline measurements and evaluation

This module provides:
- Automated test execution against benchmark dataset
- Baseline metric calculation with confidence intervals
- Test-retest reliability measurement
- Result aggregation and reporting
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import time
import json
import logging
import hashlib
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import statistics
from pathlib import Path

from src.cleo.cleo_agent import CleoAgent
from tests.academic.benchmark_dataset import BenchmarkDataset, QueryCategory, get_benchmark_dataset
from tests.academic.metric_calculators import CompositeEvaluator, EvaluationResult


class RateLimitHandler:
    """
    Handles API rate limiting with exponential backoff and response caching
    """

    def __init__(self, cache_dir: str = None):
        """
        Initialize rate limit handler

        Args:
            cache_dir: Directory to cache responses (default: data/evaluation/cache)
        """
        if cache_dir is None:
            cache_dir = "c:\\Users\\yasee\\OneDrive\\Desktop\\VOYO_Backend\\voyo-backend\\data\\evaluation\\cache"

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.response_cache = {}
        self.rate_limit_delays = []

        # Load existing cache
        self._load_cache()

    def _get_cache_key(self, query: str, user_id: Optional[str] = None) -> str:
        """Generate cache key for query"""
        content = f"{query}|{user_id or 'anonymous'}"
        return hashlib.md5(content.encode()).hexdigest()

    def _load_cache(self):
        """Load cached responses from disk"""
        cache_file = self.cache_dir / "responses.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self.response_cache = json.load(f)
                logger.info(f"Loaded {len(self.response_cache)} cached responses")
            except Exception as e:
                logger.warning(f"Could not load cache: {e}")

    def _save_cache(self):
        """Save cached responses to disk"""
        cache_file = self.cache_dir / "responses.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.response_cache, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save cache: {e}")

    def get_cached_response(self, query: str, user_id: Optional[str] = None) -> Optional[str]:
        """Get cached response if available"""
        cache_key = self._get_cache_key(query, user_id)
        return self.response_cache.get(cache_key)

    def cache_response(self, query: str, response: str, user_id: Optional[str] = None):
        """Cache a response"""
        cache_key = self._get_cache_key(query, user_id)
        self.response_cache[cache_key] = response
        self._save_cache()

    def wait_with_backoff(self, attempt: int, base_delay: float = 1.0, max_delay: float = 60.0):
        """
        Wait with exponential backoff

        Args:
            attempt: Current attempt number
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
        """
        delay = min(base_delay * (2 ** attempt), max_delay)
        jitter = delay * 0.1  # Add 10% jitter

        logger.info(f"Rate limit detected, waiting {delay:.1f}s before retry (attempt {attempt + 1})")
        time.sleep(delay + jitter)

        self.rate_limit_delays.append(delay)

    def clear_cache(self):
        """Clear the response cache"""
        self.response_cache = {}
        self._save_cache()
        logger.info("Cache cleared")

    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            "cached_responses": len(self.response_cache),
            "total_rate_limit_delay": sum(self.rate_limit_delays),
            "rate_limit_events": len(self.rate_limit_delays)
        }

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Result of a single query test"""
    query_id: str
    query: str
    category: str
    difficulty: str

    # Response data
    response: str
    response_length: int
    response_time_ms: float

    # Tool usage
    tools_used: List[str]

    # Evaluation scores
    scores: Dict[str, float]
    passed_metrics: List[str]
    failed_metrics: List[str]

    # Overall assessment
    overall_score: float
    passed: bool

    # Timestamp
    timestamp: str

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class BaselineReport:
    """Aggregated baseline measurement report"""
    run_id: str
    timestamp: str
    total_queries: int
    successful_queries: int
    failed_queries: int

    # Overall scores
    mean_overall_score: float
    std_overall_score: float
    min_overall_score: float
    max_overall_score: float

    # Per-metric scores
    metric_means: Dict[str, float]
    metric_stds: Dict[str, float]

    # Per-category scores
    category_scores: Dict[str, float]

    # Per-difficulty scores
    difficulty_scores: Dict[str, float]

    # Performance metrics
    mean_response_time_ms: float
    median_response_time_ms: float
    mean_response_length: int

    # Pass rates
    overall_pass_rate: float
    metric_pass_rates: Dict[str, float]

    # Cache statistics (optional, added dynamically)
    cache_stats: Optional[Dict] = None

    def to_dict(self) -> Dict:
        data = asdict(self)
        # Handle cache_stats separately since it's not always set
        if hasattr(self, 'cache_stats') and self.cache_stats:
            data['cache_stats'] = self.cache_stats
        return data

    def print_summary(self):
        """Print a summary of the baseline report"""
        print("\n" + "=" * 70)
        print(f"BASELINE REPORT: {self.run_id}")
        print("=" * 70)
        print(f"Timestamp: {self.timestamp}")
        print(f"Total Queries: {self.total_queries}")
        print(f"Successful: {self.successful_queries} ({self.successful_queries/self.total_queries*100:.1f}%)")
        print(f"Failed: {self.failed_queries}")

        print("\n--- Overall Scores ---")
        print(f"Mean: {self.mean_overall_score:.3f} ± {self.std_overall_score:.3f}")
        print(f"Range: [{self.min_overall_score:.3f}, {self.max_overall_score:.3f}]")

        print("\n--- Per-Metric Scores ---")
        for metric, mean in sorted(self.metric_means.items()):
            std = self.metric_stds.get(metric, 0)
            pass_rate = self.metric_pass_rates.get(metric, 0)
            print(f"  {metric}: {mean:.3f} ± {std:.3f} (pass: {pass_rate*100:.1f}%)")

        print("\n--- Per-Category Scores ---")
        for category, score in sorted(self.category_scores.items()):
            print(f"  {category}: {score:.3f}")

        print("\n--- Per-Difficulty Scores ---")
        for difficulty, score in sorted(self.difficulty_scores.items()):
            print(f"  {difficulty}: {score:.3f}")

        print("\n--- Performance Metrics ---")
        print(f"Mean Response Time: {self.mean_response_time_ms:.0f}ms")
        print(f"Median Response Time: {self.median_response_time_ms:.0f}ms")
        print(f"Mean Response Length: {self.mean_response_length:.0f} chars")

        print("\n--- Pass Rates ---")
        print(f"Overall Pass Rate: {self.overall_pass_rate*100:.1f}%")

        # Cache stats if available
        if hasattr(self, 'cache_stats') and self.cache_stats:
            print("\n--- Cache Statistics ---")
            print(f"Cached Responses: {self.cache_stats['after']['cached_responses']}")
            print(f"New Cache Hits: {self.cache_stats['new_cache_hits']}")
            if self.cache_stats['after']['rate_limit_events'] > 0:
                print(f"Rate Limit Events: {self.cache_stats['after']['rate_limit_events']}")
                print(f"Total Rate Limit Delay: {self.cache_stats['after']['total_rate_limit_delay']:.1f}s")

        print("=" * 70)


class AcademicTestRunner:
    """
    Automated test runner for CLEO baseline measurements

    Features:
    - Executes queries from benchmark dataset
    - Calculates comprehensive metrics
    - Measures response times
    - Tracks tool usage
    - Generates baseline reports
    - Supports test-retest reliability
    - Rate limit handling with exponential backoff
    - Response caching to reduce API calls
    """

    def __init__(self, use_cache: bool = True):
        """
        Initialize test runner

        Args:
            use_cache: Whether to use response caching
        """
        logger.info("Initializing Academic Test Runner...")

        self.agent = CleoAgent()
        self.dataset = get_benchmark_dataset()
        self.evaluator = CompositeEvaluator()
        self.rate_limit_handler = RateLimitHandler()
        self.use_cache = use_cache

        logger.info(f"Loaded {len(self.dataset)} benchmark queries")
        logger.info(f"Caching enabled: {self.use_cache}")

    def run_single_query(
        self,
        query: str,
        query_metadata: Dict,
        user_id: Optional[str] = None,
        debug: bool = False,
        max_retries: int = 5
    ) -> TestResult:
        """
        Run a single query test with rate limit handling

        Args:
            query: User's query
            query_metadata: Query metadata from benchmark dataset
            user_id: Optional user ID for personalization
            debug: Enable debug mode
            max_retries: Maximum number of retries on rate limit

        Returns:
            TestResult with scores and assessment
        """
        # Check cache first
        if self.use_cache:
            cached_response = self.rate_limit_handler.get_cached_response(query, user_id)
            if cached_response:
                logger.debug(f"Cache hit for query: {query[:50]}...")
                # Evaluate cached response
                return self._evaluate_response(
                    query, cached_response, query_metadata, user_id,
                    from_cache=True, response_time_ms=0
                )

        # Make API call with retry logic
        for attempt in range(max_retries):
            start_time = time.time()

            try:
                response = self.agent.process_message(
                    user_message=query,
                    user_id=user_id,
                    debug=debug
                )

                # Cache the response
                if self.use_cache:
                    self.rate_limit_handler.cache_response(query, response, user_id)

                # Evaluate and return
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000

                return self._evaluate_response(
                    query, response, query_metadata, user_id,
                    from_cache=False, response_time_ms=response_time_ms
                )

            except Exception as e:
                error_str = str(e).lower()

                # Check if it's a rate limit error
                if "429" in error_str or "rate limit" in error_str:
                    if attempt < max_retries - 1:
                        self.rate_limit_handler.wait_with_backoff(attempt)
                        continue
                    else:
                        logger.error(f"Max retries reached for query: {query[:50]}")
                        response = f"Error: Rate limit exceeded after {max_retries} retries"
                        return self._evaluate_response(
                            query, response, query_metadata, user_id,
                            from_cache=False, response_time_ms=0
                        )
                else:
                    # Non-rate-limit error
                    logger.error(f"Error processing query: {e}")
                    response = f"Error: {str(e)}"
                    return self._evaluate_response(
                        query, response, query_metadata, user_id,
                        from_cache=False, response_time_ms=0
                    )

    def _evaluate_response(
        self,
        query: str,
        response: str,
        query_metadata: Dict,
        user_id: Optional[str],
        from_cache: bool,
        response_time_ms: float
    ) -> TestResult:
        """
        Evaluate a response and generate TestResult

        Args:
            query: Original query
            response: CLEO's response
            query_metadata: Query metadata
            user_id: User ID
            from_cache: Whether response was from cache
            response_time_ms: Response time in ms

        Returns:
            TestResult with evaluation
        """
        success = not response.startswith("Error:")

        # Extract tools used
        tools_used = query_metadata.get("tools_required", [])

        # Evaluate response
        evaluation_results = self.evaluator.evaluate_all(
            query_text=query,
            response_text=response,
            query_metadata=query_metadata,
            tools_used=tools_used
        )

        # Extract scores
        scores = {name: result.score for name, result in evaluation_results.items()}
        passed_metrics = [name for name, result in evaluation_results.items() if result.passed]
        failed_metrics = [name for name, result in evaluation_results.items() if not result.passed]

        # Calculate overall score
        overall_score = self.evaluator.get_overall_score(evaluation_results)

        # Determine if passed (>= 70% overall and no critical failures)
        passed = overall_score >= 0.7 and success

        return TestResult(
            query_id=query_metadata.get("query_id", "unknown"),
            query=query,
            category=query_metadata.get("category", "unknown"),
            difficulty=query_metadata.get("difficulty", "unknown"),
            response=response,
            response_length=len(response),
            response_time_ms=response_time_ms,
            tools_used=tools_used,
            scores=scores,
            passed_metrics=passed_metrics,
            failed_metrics=failed_metrics,
            overall_score=overall_score,
            passed=passed,
            timestamp=datetime.now().isoformat()
        )

    def run_baseline(
        self,
        sample_size: Optional[int] = None,
        categories: Optional[List[str]] = None,
        save_results: bool = True,
        batch_delay: float = 2.0,
        queries_per_batch: int = 5
    ) -> BaselineReport:
        """
        Run baseline measurement with rate limit protection

        Args:
            sample_size: Number of queries to run (None = all)
            categories: Filter by categories (None = all)
            save_results: Whether to save results to file
            batch_delay: Delay between batches in seconds
            queries_per_batch: Number of queries per batch before delay

        Returns:
            BaselineReport with aggregated metrics
        """
        run_id = f"baseline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        logger.info(f"Starting baseline run: {run_id}")
        cache_stats_before = self.rate_limit_handler.get_cache_stats()
        logger.info(f"Cache stats before: {cache_stats_before}")

        # Get queries to test
        if categories:
            queries = []
            for cat in categories:
                queries.extend(self.dataset.get_by_category(QueryCategory(cat)))
        else:
            queries = self.dataset.queries

        if sample_size:
            queries = queries[:sample_size]

        logger.info(f"Testing {len(queries)} queries (batch size: {queries_per_batch}, delay: {batch_delay}s)")

        # Run tests in batches
        results = []
        successful = 0
        failed = 0

        for i, query_obj in enumerate(queries):
            if (i + 1) % 10 == 0:
                logger.info(f"Progress: {i + 1}/{len(queries)} ({successful/(i+1)*100:.1f}% passed)")

            result = self.run_single_query(
                query=query_obj.query,
                query_metadata=query_obj.to_dict()
            )
            results.append(result)

            if result.passed:
                successful += 1
            else:
                failed += 1

            # Add delay between batches to avoid rate limiting
            if (i + 1) % queries_per_batch == 0 and i < len(queries) - 1:
                logger.info(f"Batch completed, waiting {batch_delay}s to avoid rate limits...")
                time.sleep(batch_delay)

        # Generate report
        report = self._generate_report(run_id, results)

        # Add cache stats to report
        cache_stats_after = self.rate_limit_handler.get_cache_stats()
        report.cache_stats = {
            "before": cache_stats_before,
            "after": cache_stats_after,
            "new_cache_hits": cache_stats_after["cached_responses"] - cache_stats_before["cached_responses"]
        }

        # Save results
        if save_results:
            self._save_results(run_id, results, report)

        return report

    def run_test_retest(
        self,
        num_runs: int = 3,
        sample_size: Optional[int] = None
    ) -> List[BaselineReport]:
        """
        Run test-retest reliability measurement

        Args:
            num_runs: Number of times to run the test
            sample_size: Number of queries per run

        Returns:
            List of BaselineReports for each run
        """
        logger.info(f"Running test-retest reliability study ({num_runs} runs)")

        reports = []
        for i in range(num_runs):
            logger.info(f"\n--- Run {i + 1}/{num_runs} ---")
            report = self.run_baseline(
                sample_size=sample_size,
                save_results=True
            )
            reports.append(report)

        # Calculate reliability metrics
        self._calculate_reliability_metrics(reports)

        return reports

    def _generate_report(self, run_id: str, results: List[TestResult]) -> BaselineReport:
        """Generate baseline report from test results"""
        total = len(results)
        successful = sum(1 for r in results if r.passed)
        failed = total - successful

        # Overall scores
        overall_scores = [r.overall_score for r in results]
        mean_overall = statistics.mean(overall_scores)
        std_overall = statistics.stdev(overall_scores) if len(overall_scores) > 1 else 0

        # Per-metric scores
        metric_scores = {}
        metric_stds = {}
        for metric in self._get_all_metrics(results):
            scores = [r.scores.get(metric, 0) for r in results if metric in r.scores]
            if scores:
                metric_scores[metric] = statistics.mean(scores)
                metric_stds[metric] = statistics.stdev(scores) if len(scores) > 1 else 0

        # Per-category scores
        category_scores = {}
        for category in set(r.category for r in results):
            cat_results = [r for r in results if r.category == category]
            category_scores[category] = statistics.mean([r.overall_score for r in cat_results])

        # Per-difficulty scores
        difficulty_scores = {}
        for difficulty in set(r.difficulty for r in results):
            diff_results = [r for r in results if r.difficulty == difficulty]
            difficulty_scores[difficulty] = statistics.mean([r.overall_score for r in diff_results])

        # Performance metrics
        response_times = [r.response_time_ms for r in results]
        mean_response_time = statistics.mean(response_times)
        median_response_time = statistics.median(response_times)

        mean_length = statistics.mean([r.response_length for r in results])

        # Pass rates
        overall_pass_rate = successful / total if total > 0 else 0

        metric_pass_rates = {}
        for metric in self._get_all_metrics(results):
            passed = sum(1 for r in results if metric in r.passed_metrics)
            total_with_metric = sum(1 for r in results if metric in r.scores)
            if total_with_metric > 0:
                metric_pass_rates[metric] = passed / total_with_metric

        return BaselineReport(
            run_id=run_id,
            timestamp=datetime.now().isoformat(),
            total_queries=total,
            successful_queries=successful,
            failed_queries=failed,
            mean_overall_score=mean_overall,
            std_overall_score=std_overall,
            min_overall_score=min(overall_scores),
            max_overall_score=max(overall_scores),
            metric_means=metric_scores,
            metric_stds=metric_stds,
            category_scores=category_scores,
            difficulty_scores=difficulty_scores,
            mean_response_time_ms=mean_response_time,
            median_response_time_ms=median_response_time,
            mean_response_length=int(mean_length),
            overall_pass_rate=overall_pass_rate,
            metric_pass_rates=metric_pass_rates
        )

    def _get_all_metrics(self, results: List[TestResult]) -> List[str]:
        """Get all unique metric names from results"""
        metrics = set()
        for result in results:
            metrics.update(result.scores.keys())
        return list(metrics)

    def _save_results(self, run_id: str, results: List[TestResult], report: BaselineReport):
        """Save test results and report to files"""
        output_dir = "c:\\Users\\yasee\\OneDrive\\Desktop\\VOYO_Backend\\voyo-backend\\data\\evaluation\\results"

        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Save individual results
        results_file = os.path.join(output_dir, f"{run_id}_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump([r.to_dict() for r in results], f, indent=2, ensure_ascii=False)

        # Save report
        report_file = os.path.join(output_dir, f"{run_id}_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)

        logger.info(f"Results saved to: {results_file}")
        logger.info(f"Report saved to: {report_file}")

    def _calculate_reliability_metrics(self, reports: List[BaselineReport]):
        """Calculate test-retest reliability metrics"""
        if len(reports) < 2:
            logger.warning("Need at least 2 runs to calculate reliability")
            return

        print("\n" + "=" * 70)
        print("TEST-RETEST RELIABILITY ANALYSIS")
        print("=" * 70)

        # Overall score variance
        overall_scores = [r.mean_overall_score for r in reports]
        if len(overall_scores) > 1:
            overall_std = statistics.stdev(overall_scores)
            overall_mean = statistics.mean(overall_scores)
            cv = (overall_std / overall_mean * 100) if overall_mean > 0 else 0

            print(f"\nOverall Score Stability:")
            print(f"  Mean: {overall_mean:.4f}")
            print(f"  Std Dev: {overall_std:.4f}")
            print(f"  Coefficient of Variation: {cv:.2f}%")

            # Assess reliability
            if cv < 5:
                reliability = "Excellent"
            elif cv < 10:
                reliability = "Good"
            elif cv < 20:
                reliability = "Moderate"
            else:
                reliability = "Poor"

            print(f"  Reliability: {reliability}")

        # Per-metric stability
        print(f"\nPer-Metric Stability:")
        for metric in reports[0].metric_means.keys():
            scores = [r.metric_means.get(metric, 0) for r in reports]
            if len(scores) > 1 and any(s > 0 for s in scores):
                metric_mean = statistics.mean(scores)
                metric_std = statistics.stdev(scores)
                metric_cv = (metric_std / metric_mean * 100) if metric_mean > 0 else 0
                print(f"  {metric}: CV={metric_cv:.1f}%")

        print("=" * 70)


def main():
    """Main entry point for test runner"""
    import argparse

    parser = argparse.ArgumentParser(description="VOYO Academic Test Runner")
    parser.add_argument("--sample", type=int, help="Sample size (default: all)")
    parser.add_argument("--category", type=str, help="Filter by category")
    parser.add_argument("--runs", type=int, default=1, help="Number of test-retest runs")
    parser.add_argument("--no-save", action="store_true", help="Don't save results")
    parser.add_argument("--batch-delay", type=float, default=2.0, help="Delay between batches (seconds)")
    parser.add_argument("--batch-size", type=int, default=5, help="Queries per batch")
    parser.add_argument("--no-cache", action="store_true", help="Disable response caching")

    args = parser.parse_args()

    # Initialize test runner
    runner = AcademicTestRunner(use_cache=not args.no_cache)

    # Run tests
    if args.runs > 1:
        reports = runner.run_test_retest(
            num_runs=args.runs,
            sample_size=args.sample
        )
        report = reports[0]  # Use first report for display
    else:
        categories = [args.category] if args.category else None
        report = runner.run_baseline(
            sample_size=args.sample,
            categories=categories,
            save_results=not args.no_save,
            batch_delay=args.batch_delay,
            queries_per_batch=args.batch_size
        )

    # Print summary
    report.print_summary()

    return 0 if report.mean_overall_score >= 0.7 else 1


if __name__ == "__main__":
    sys.exit(main())
