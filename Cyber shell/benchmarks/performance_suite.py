"""
CyberShell Performance Benchmarking Suite
==========================================

Purpose: Comprehensive performance testing and SLA validation
Benchmarks:
- Detection latency (target: <15ms per event)
- Throughput (events/second)
- Resource usage (CPU, memory)
- Scalability tests (1K, 10K, 100K events)
- Comparison with commercial EDR baseline
"""

import time
import json
import psutil
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict
import sys
sys.path.append(str(Path(__file__).parent.parent))

from parser.feature_extractor import FeatureRow
from model.detect import HybridDetector


@dataclass
class BenchmarkResult:
    """Result from a benchmark test"""
    test_name: str
    num_events: int
    total_time_sec: float
    avg_latency_ms: float
    median_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    max_latency_ms: float
    throughput_eps: float  # events per second
    cpu_usage_percent: float
    memory_usage_mb: float
    sla_compliance: bool  # True if avg latency < 15ms
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def print_summary(self):
        """Print human-readable summary"""
        print(f"\n{'='*60}")
        print(f"BENCHMARK: {self.test_name}")
        print(f"{'='*60}")
        print(f"Events Processed:    {self.num_events:,}")
        print(f"Total Time:          {self.total_time_sec:.2f}s")
        print(f"Throughput:          {self.throughput_eps:.2f} events/sec")
        print(f"\nLatency Statistics:")
        print(f"  Average:           {self.avg_latency_ms:.2f}ms")
        print(f"  Median:            {self.median_latency_ms:.2f}ms")
        print(f"  P95:               {self.p95_latency_ms:.2f}ms")
        print(f"  P99:               {self.p99_latency_ms:.2f}ms")
        print(f"  Maximum:           {self.max_latency_ms:.2f}ms")
        print(f"\nResource Usage:")
        print(f"  CPU:               {self.cpu_usage_percent:.1f}%")
        print(f"  Memory:            {self.memory_usage_mb:.1f} MB")
        print(f"\nSLA Compliance (< 15ms avg): {'✅ PASS' if self.sla_compliance else '❌ FAIL'}")
        print(f"{'='*60}")


class BenchmarkSuite:
    """Comprehensive benchmark testing suite"""
    
    def __init__(self, model_path: str = "model/model.pkl"):
        self.detector = HybridDetector(
            model_path=model_path,
            enable_explainability=False,  # Disable for pure performance
            enable_mitre_mapping=False
        )
        self.process = psutil.Process()
    
    def benchmark_latency(self, features: List[FeatureRow], 
                          test_name: str = "Latency Test") -> BenchmarkResult:
        """
        Benchmark detection latency on a set of feature rows.
        
        Args:
            features: List of FeatureRow objects to process
            test_name: Name of the test
            
        Returns:
            BenchmarkResult with detailed statistics
        """
        num_events = len(features)
        latencies = []
        
        # Warm-up run
        _ = self.detector.detect(features[0])
        
        # Capture initial resource usage
        cpu_start = self.process.cpu_percent()
        mem_start = self.process.memory_info().rss / 1024 / 1024  # MB
        
        # Benchmark loop
        start_time = time.perf_counter()
        
        for feature in features:
            event_start = time.perf_counter()
            _ = self.detector.detect(feature)
            event_end = time.perf_counter()
            latencies.append((event_end - event_start) * 1000)  # ms
        
        total_time = time.perf_counter() - start_time
        
        # Capture final resource usage
        cpu_end = self.process.cpu_percent()
        mem_end = self.process.memory_info().rss / 1024 / 1024
        
        # Calculate statistics
        latencies_array = np.array(latencies)
        avg_latency = np.mean(latencies_array)
        median_latency = np.median(latencies_array)
        p95_latency = np.percentile(latencies_array, 95)
        p99_latency = np.percentile(latencies_array, 99)
        max_latency = np.max(latencies_array)
        throughput = num_events / total_time if total_time > 0 else 0
        
        cpu_usage = (cpu_start + cpu_end) / 2
        memory_usage = (mem_start + mem_end) / 2
        
        sla_compliant = avg_latency < 15.0  # Target SLA: <15ms
        
        return BenchmarkResult(
            test_name=test_name,
            num_events=num_events,
            total_time_sec=total_time,
            avg_latency_ms=avg_latency,
            median_latency_ms=median_latency,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            max_latency_ms=max_latency,
            throughput_eps=throughput,
            cpu_usage_percent=cpu_usage,
            memory_usage_mb=memory_usage,
            sla_compliance=sla_compliant
        )
    
    def benchmark_throughput(self, num_events: int = 10000) -> BenchmarkResult:
        """
        Benchmark maximum throughput with synthetic data.
        
        Args:
            num_events: Number of synthetic events to process
            
        Returns:
            BenchmarkResult
        """
        # Generate synthetic feature rows
        features = self._generate_synthetic_features(num_events)
        
        return self.benchmark_latency(
            features, 
            test_name=f"Throughput Test ({num_events:,} events)"
        )
    
    def benchmark_scalability(self) -> List[BenchmarkResult]:
        """
        Benchmark scalability across different event volumes.
        Tests: 1K, 10K, 100K events
        
        Returns:
            List of BenchmarkResults
        """
        results = []
        
        for scale in [1_000, 10_000, 100_000]:
            print(f"\n[INFO] Running scalability test with {scale:,} events...")
            result = self.benchmark_throughput(scale)
            results.append(result)
            result.print_summary()
        
        return results
    
    def benchmark_resource_stress(self, duration_sec: int = 60) -> BenchmarkResult:
        """
        Stress test with continuous load for specified duration.
        
        Args:
            duration_sec: How long to run the stress test
            
        Returns:
            BenchmarkResult
        """
        print(f"\n[INFO] Running {duration_sec}s stress test...")
        
        latencies = []
        event_count = 0
        start_time = time.perf_counter()
        
        # Resource monitoring
        cpu_samples = []
        mem_samples = []
        
        # Generate synthetic features
        features = self._generate_synthetic_features(1000)
        feature_idx = 0
        
        while (time.perf_counter() - start_time) < duration_sec:
            # Cycle through features
            feature = features[feature_idx % len(features)]
            feature_idx += 1
            
            # Detect
            event_start = time.perf_counter()
            _ = self.detector.detect(feature)
            event_end = time.perf_counter()
            
            latencies.append((event_end - event_start) * 1000)
            event_count += 1
            
            # Sample resources every 100 events
            if event_count % 100 == 0:
                cpu_samples.append(self.process.cpu_percent())
                mem_samples.append(self.process.memory_info().rss / 1024 / 1024)
        
        total_time = time.perf_counter() - start_time
        
        # Calculate statistics
        latencies_array = np.array(latencies)
        avg_latency = np.mean(latencies_array)
        median_latency = np.median(latencies_array)
        p95_latency = np.percentile(latencies_array, 95)
        p99_latency = np.percentile(latencies_array, 99)
        max_latency = np.max(latencies_array)
        throughput = event_count / total_time
        
        avg_cpu = np.mean(cpu_samples) if cpu_samples else 0
        avg_mem = np.mean(mem_samples) if mem_samples else 0
        
        return BenchmarkResult(
            test_name=f"Stress Test ({duration_sec}s)",
            num_events=event_count,
            total_time_sec=total_time,
            avg_latency_ms=avg_latency,
            median_latency_ms=median_latency,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            max_latency_ms=max_latency,
            throughput_eps=throughput,
            cpu_usage_percent=avg_cpu,
            memory_usage_mb=avg_mem,
            sla_compliance=(avg_latency < 15.0)
        )
    
    def _generate_synthetic_features(self, count: int) -> List[FeatureRow]:
        """Generate synthetic feature rows for testing"""
        features = []
        
        for i in range(count):
            features.append(FeatureRow(
                timestamp=f"2024-01-01T00:{i//60:02d}:{i%60:02d}",
                host_hash=f"host_{i % 10}",
                process_name="test.exe",
                parent_process="explorer.exe",
                cmdline_entropy=3.5 + np.random.randn() * 0.5,
                outbound_bytes_5m=int(10000 + np.random.randn() * 5000),
                unique_dst_ips_1hr=int(5 + np.random.randn() * 2),
                unique_dst_ports_1hr=int(3 + np.random.randn()),
                periodic_connection_score=0.3 + np.random.randn() * 0.1,
                file_write_rate_1m=int(10 + np.random.randn() * 5),
                file_rename_count_5m=int(2 + np.random.randn()),
                unique_extensions_written=2,
                failed_logons_10m=0,
                privilege_escalation_score=0.1,
                ransomware_score=0.2,
                exfil_score=0.15,
                c2_beacon_score=0.25,
                lateral_movement_score=0.1
            ))
        
        return features
    
    def compare_with_baseline(self, baseline_latency_ms: float = 20.0) -> Dict:
        """
        Compare CyberShell performance with a baseline (e.g., commercial EDR).
        
        Args:
            baseline_latency_ms: Baseline average latency to compare against
            
        Returns:
            Dictionary with comparison results
        """
        # Run benchmark
        result = self.benchmark_throughput(10000)
        
        # Calculate improvement
        improvement_percent = ((baseline_latency_ms - result.avg_latency_ms) / baseline_latency_ms) * 100
        
        comparison = {
            'cybershell_latency_ms': result.avg_latency_ms,
            'baseline_latency_ms': baseline_latency_ms,
            'improvement_percent': improvement_percent,
            'faster_than_baseline': result.avg_latency_ms < baseline_latency_ms,
            'speedup_factor': baseline_latency_ms / result.avg_latency_ms if result.avg_latency_ms > 0 else 0
        }
        
        print(f"\n{'='*60}")
        print("BASELINE COMPARISON")
        print(f"{'='*60}")
        print(f"CyberShell Latency:  {result.avg_latency_ms:.2f}ms")
        print(f"Baseline Latency:    {baseline_latency_ms:.2f}ms")
        print(f"Improvement:         {improvement_percent:+.1f}%")
        print(f"Speedup Factor:      {comparison['speedup_factor']:.2f}x")
        print(f"{'='*60}")
        
        return comparison


def run_full_benchmark_suite(output_dir: str = "benchmarks/results"):
    """
    Run complete benchmark suite and save results.
    
    Args:
        output_dir: Directory to save benchmark results
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    suite = BenchmarkSuite()
    
    print("\n" + "="*60)
    print(" CYBERSHELL PERFORMANCE BENCHMARK SUITE")
    print("="*60)
    
    all_results = {}
    
    # Test 1: Scalability
    print("\n[1/3] Running scalability benchmarks...")
    scalability_results = suite.benchmark_scalability()
    all_results['scalability'] = [r.to_dict() for r in scalability_results]
    
    # Test 2: Stress Test
    print("\n[2/3] Running 60s stress test...")
    stress_result = suite.benchmark_resource_stress(duration_sec=60)
    stress_result.print_summary()
    all_results['stress_test'] = stress_result.to_dict()
    
    # Test 3: Baseline Comparison
    print("\n[3/3] Comparing with baseline (commercial EDR: 20ms avg)...")
    comparison = suite.compare_with_baseline(baseline_latency_ms=20.0)
    all_results['baseline_comparison'] = comparison
    
    # Save results
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_file = output_path / f"benchmark_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n✅ Results saved to: {results_file}")
    
    return all_results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CyberShell Performance Benchmarks")
    parser.add_argument("--test", choices=['latency', 'throughput', 'scalability', 'stress', 'full'],
                        default='full', help="Benchmark test to run")
    parser.add_argument("--events", type=int, default=10000,
                        help="Number of events for throughput test")
    parser.add_argument("--duration", type=int, default=60,
                        help="Duration in seconds for stress test")
    parser.add_argument("--output", default="benchmarks/results",
                        help="Output directory for results")
    
    args = parser.parse_args()
    
    suite = BenchmarkSuite()
    
    if args.test == 'throughput':
        result = suite.benchmark_throughput(args.events)
        result.print_summary()
    
    elif args.test == 'scalability':
        suite.benchmark_scalability()
    
    elif args.test == 'stress':
        result = suite.benchmark_resource_stress(args.duration)
        result.print_summary()
    
    elif args.test == 'full':
        run_full_benchmark_suite(args.output)
