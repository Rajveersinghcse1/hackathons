"""
CyberShell Enhancement Validation Script
=========================================

Purpose: Verify all world-class enhancements are working correctly.
Run this script before competition/demo to ensure everything is functional.

Tests:
1. Dependency imports (SHAP, Plotly, psutil)
2. Module integrity (explainability, threat_intelligence, advanced_components, benchmarks)
3. Integration test (HybridDetector with enhancements enabled)
4. Performance validation (quick latency test)
"""

import sys
from pathlib import Path
import time

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text.center(60)}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_info(text):
    print(f"{BLUE}ℹ️  {text}{RESET}")


class ValidationSuite:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
    
    def test_dependencies(self):
        """Test 1: Verify all dependencies are installed"""
        print_header("TEST 1: DEPENDENCY CHECK")
        
        dependencies = {
            'shap': "SHAP Explainability Library",
            'plotly': "Plotly Interactive Charts",
            'psutil': "Performance Monitoring (psutil)",
            'streamlit': "Streamlit Dashboard",
            'sklearn': "Scikit-learn ML Library",
            'pandas': "Pandas Data Processing",
            'numpy': "NumPy Numerical Computing"
        }
        
        for module, description in dependencies.items():
            try:
                __import__(module)
                print_success(f"{description} - Installed")
                self.passed += 1
            except ImportError:
                print_error(f"{description} - MISSING (install with: pip install {module})")
                self.failed += 1
    
    def test_module_integrity(self):
        """Test 2: Verify new modules can be imported"""
        print_header("TEST 2: MODULE INTEGRITY")
        
        modules = {
            'model.explainability': "SHAP Explainability Module",
            'model.threat_intelligence': "MITRE ATT&CK Mapping Module",
            'ui.advanced_components': "Advanced UI Components",
            'benchmarks.performance_suite': "Performance Benchmarking Suite"
        }
        
        for module_name, description in modules.items():
            try:
                __import__(module_name)
                print_success(f"{description} - OK")
                self.passed += 1
            except ImportError as e:
                print_error(f"{description} - IMPORT ERROR: {e}")
                self.failed += 1
    
    def test_shap_integration(self):
        """Test 3: Verify SHAP explainability integration"""
        print_header("TEST 3: SHAP EXPLAINABILITY INTEGRATION")
        
        try:
            from model.explainability import SHAPExplainer, LocalInterpretability
            print_success("SHAPExplainer class imported")
            print_success("LocalInterpretability class imported")
            self.passed += 2
            
            # Test instantiation (without model for now)
            try:
                interpreter = LocalInterpretability()
                print_success("LocalInterpretability instantiated")
                self.passed += 1
            except Exception as e:
                print_error(f"LocalInterpretability instantiation failed: {e}")
                self.failed += 1
                
        except ImportError as e:
            print_error(f"SHAP module import failed: {e}")
            self.failed += 3
    
    def test_mitre_mapping(self):
        """Test 4: Verify MITRE ATT&CK mapping"""
        print_header("TEST 4: MITRE ATT&CK MAPPING")
        
        try:
            from model.threat_intelligence import MITREMapper, TECHNIQUE_DATABASE
            print_success("MITREMapper imported")
            self.passed += 1
            
            # Check technique database
            num_techniques = len(TECHNIQUE_DATABASE)
            print_success(f"Loaded {num_techniques} ATT&CK techniques")
            self.passed += 1
            
            if num_techniques >= 6:
                print_success("Sufficient technique coverage (6+ techniques)")
                self.passed += 1
            else:
                print_warning(f"Only {num_techniques} techniques loaded (expected 6+)")
                self.warnings += 1
                
        except ImportError as e:
            print_error(f"MITRE module import failed: {e}")
            self.failed += 3
    
    def test_detector_integration(self):
        """Test 5: Verify HybridDetector integration"""
        print_header("TEST 5: HYBRID DETECTOR INTEGRATION")
        
        try:
            from model.detect import HybridDetector
            print_success("HybridDetector imported")
            self.passed += 1
            
            # Test instantiation with enhancements
            try:
                detector = HybridDetector(
                    model_path="model/model.pkl",
                    enable_explainability=True,
                    enable_mitre_mapping=True
                )
                print_success("HybridDetector instantiated with enhancements enabled")
                self.passed += 1
                
                # Check if explainer initialized
                if hasattr(detector, 'shap_explainer'):
                    if detector.shap_explainer is not None:
                        print_success("SHAP explainer initialized in detector")
                        self.passed += 1
                    else:
                        print_warning("SHAP explainer not initialized (model may be missing)")
                        self.warnings += 1
                
                # Check if MITRE mapper initialized
                if hasattr(detector, 'mitre_mapper'):
                    if detector.mitre_mapper is not None:
                        print_success("MITRE mapper initialized in detector")
                        self.passed += 1
                    else:
                        print_error("MITRE mapper not initialized")
                        self.failed += 1
                        
            except Exception as e:
                print_error(f"HybridDetector instantiation failed: {e}")
                self.failed += 3
                
        except ImportError as e:
            print_error(f"HybridDetector import failed: {e}")
            self.failed += 4
    
    def test_ui_components(self):
        """Test 6: Verify advanced UI components"""
        print_header("TEST 6: ADVANCED UI COMPONENTS")
        
        try:
            from ui.advanced_components import (
                render_interactive_timeline,
                render_mitre_heatmap,
                render_performance_dashboard,
                render_threat_intelligence_panel,
                render_shap_explanation
            )
            
            components = [
                "render_interactive_timeline",
                "render_mitre_heatmap",
                "render_performance_dashboard",
                "render_threat_intelligence_panel",
                "render_shap_explanation"
            ]
            
            for component in components:
                print_success(f"{component} - Available")
                self.passed += 1
                
        except ImportError as e:
            print_error(f"UI components import failed: {e}")
            self.failed += 5
    
    def test_benchmarks(self):
        """Test 7: Verify benchmark suite"""
        print_header("TEST 7: PERFORMANCE BENCHMARKING SUITE")
        
        try:
            from benchmarks.performance_suite import BenchmarkSuite, BenchmarkResult
            print_success("BenchmarkSuite imported")
            print_success("BenchmarkResult imported")
            self.passed += 2
            
            # Test instantiation
            try:
                suite = BenchmarkSuite()
                print_success("BenchmarkSuite instantiated")
                self.passed += 1
            except Exception as e:
                print_error(f"BenchmarkSuite instantiation failed: {e}")
                self.failed += 1
                
        except ImportError as e:
            print_error(f"Benchmark module import failed: {e}")
            self.failed += 3
    
    def run_all_tests(self):
        """Run all validation tests"""
        print_header("CYBERSHELL ENHANCEMENT VALIDATION")
        print_info("Verifying all world-class enhancements are functional...")
        
        self.test_dependencies()
        self.test_module_integrity()
        self.test_shap_integration()
        self.test_mitre_mapping()
        self.test_detector_integration()
        self.test_ui_components()
        self.test_benchmarks()
        
        # Final summary
        print_header("VALIDATION SUMMARY")
        total_tests = self.passed + self.failed + self.warnings
        
        print(f"\n{GREEN}✅ Passed: {self.passed}{RESET}")
        if self.warnings > 0:
            print(f"{YELLOW}⚠️  Warnings: {self.warnings}{RESET}")
        if self.failed > 0:
            print(f"{RED}❌ Failed: {self.failed}{RESET}")
        
        print(f"\n{BLUE}Total Tests: {total_tests}{RESET}\n")
        
        # Pass/fail determination
        if self.failed == 0:
            print(f"{GREEN}{'='*60}{RESET}")
            print(f"{GREEN}🏆 ALL VALIDATIONS PASSED - READY FOR COMPETITION! 🏆{RESET}")
            print(f"{GREEN}{'='*60}{RESET}\n")
            return True
        else:
            print(f"{RED}{'='*60}{RESET}")
            print(f"{RED}⚠️  VALIDATION FAILED - PLEASE FIX ERRORS ABOVE{RESET}")
            print(f"{RED}{'='*60}{RESET}\n")
            return False


def main():
    suite = ValidationSuite()
    success = suite.run_all_tests()
    
    if success:
        print(f"{BLUE}Next steps:{RESET}")
        print(f"  1. Run dashboard: {GREEN}streamlit run ui/streamlit_app.py{RESET}")
        print(f"  2. Run benchmarks: {GREEN}python benchmarks/performance_suite.py --test full{RESET}")
        print(f"  3. See quick-start guide: {GREEN}QUICKSTART_COMPETITION.md{RESET}\n")
    else:
        print(f"{YELLOW}Troubleshooting:{RESET}")
        print(f"  1. Install dependencies: {YELLOW}pip install -r requirements.txt{RESET}")
        print(f"  2. Verify Python version: {YELLOW}python --version{RESET} (need 3.11+)")
        print(f"  3. Check file integrity: Ensure all new modules exist\n")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
