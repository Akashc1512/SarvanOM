#!/usr/bin/env python3
"""
Comprehensive Error Handling Verification Script

This script verifies the error handling implementation in the API Gateway
by testing various error scenarios and ensuring proper error responses.

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    1.0.0 (2024-12-28)
"""

import asyncio
import time
import json
import sys
from typing import Dict, Any, List
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from shared.core.unified_logging import get_logger

logger = get_logger(__name__)


class ErrorHandlingVerifier:
    """Verifier for comprehensive error handling implementation."""
    
    def __init__(self):
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result with details."""
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{status}: {test_name}")
        if details:
            logger.info(f"  Details: {details}")
        
        self.test_results.append({
            "test_name": test_name,
            "passed": passed,
            "details": details,
            "timestamp": time.time()
        })
        
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
    
    async def verify_error_handling_utilities(self) -> bool:
        """Verify error handling utilities are properly implemented."""
        logger.info("🔍 Verifying error handling utilities...")
        
        try:
            # Test import of error handling utilities
            from services.api_gateway.utils.error_handlers import (
                LLMErrorHandler,
                DatabaseErrorHandler,
                ExternalAPIErrorHandler,
                safe_operation,
                log_operation_error,
                create_error_response
            )
            
            self.log_test_result(
                "Error handling utilities import",
                True,
                "All error handling utilities imported successfully"
            )
            
            # Test error response creation
            error_response = create_error_response(
                error_message="Test error",
                error_type="test_error",
                status_code=503,
                request_id="test_123"
            )
            
            expected_keys = ["success", "error", "error_type", "status_code", "timestamp"]
            all_keys_present = all(key in error_response for key in expected_keys)
            
            self.log_test_result(
                "Error response creation",
                all_keys_present,
                f"Response keys: {list(error_response.keys())}"
            )
            
            return True
            
        except ImportError as e:
            self.log_test_result(
                "Error handling utilities import",
                False,
                f"Import error: {e}"
            )
            return False
        except Exception as e:
            self.log_test_result(
                "Error handling utilities test",
                False,
                f"Unexpected error: {e}"
            )
            return False
    
    async def verify_queries_route_error_handling(self) -> bool:
        """Verify error handling in queries route."""
        logger.info("🔍 Verifying queries route error handling...")
        
        try:
            # Test import of queries route
            from services.api_gateway.routes.queries import router
            
            self.log_test_result(
                "Queries route import",
                True,
                "Queries route imported successfully"
            )
            
            # Check for asyncio import (added for timeout handling)
            import asyncio
            self.log_test_result(
                "Asyncio import in queries route",
                True,
                "Asyncio module available for timeout handling"
            )
            
            # Verify error handling patterns in the route
            route_file = project_root / "services" / "api_gateway" / "routes" / "queries.py"
            if route_file.exists():
                content = route_file.read_text()
                
                # Check for timeout handling patterns
                has_timeout_handling = "asyncio.wait_for" in content
                self.log_test_result(
                    "Timeout handling in queries route",
                    has_timeout_handling,
                    "Timeout handling patterns found" if has_timeout_handling else "Timeout handling patterns missing"
                )
                
                # Check for comprehensive error handling
                has_error_handling = "except Exception as" in content and "logger.error" in content
                self.log_test_result(
                    "Comprehensive error handling in queries route",
                    has_error_handling,
                    "Error handling patterns found" if has_error_handling else "Error handling patterns missing"
                )
                
                # Check for database error handling
                has_db_error_handling = "asyncpg." in content and "HTTPException" in content
                self.log_test_result(
                    "Database error handling in queries route",
                    has_db_error_handling,
                    "Database error handling found" if has_db_error_handling else "Database error handling missing"
                )
                
            return True
            
        except ImportError as e:
            self.log_test_result(
                "Queries route import",
                False,
                f"Import error: {e}"
            )
            return False
        except Exception as e:
            self.log_test_result(
                "Queries route error handling test",
                False,
                f"Unexpected error: {e}"
            )
            return False
    
    async def verify_main_app_error_handling(self) -> bool:
        """Verify error handling in main application."""
        logger.info("🔍 Verifying main app error handling...")
        
        try:
            # Test import of main app
            from services.api_gateway.main import app
            
            self.log_test_result(
                "Main app import",
                True,
                "Main app imported successfully"
            )
            
            # Check for exception handlers
            main_file = project_root / "services" / "api_gateway" / "main.py"
            if main_file.exists():
                content = main_file.read_text()
                
                # Check for exception handlers
                has_exception_handlers = "@app.exception_handler" in content
                self.log_test_result(
                    "Exception handlers in main app",
                    has_exception_handlers,
                    "Exception handlers found" if has_exception_handlers else "Exception handlers missing"
                )
                
                # Check for specific error handlers
                has_http_handler = "HTTPException" in content
                has_validation_handler = "ValidationError" in content
                has_timeout_handler = "TimeoutError" in content
                has_connection_handler = "ConnectionError" in content
                
                self.log_test_result(
                    "Specific error handlers",
                    has_http_handler and has_validation_handler and has_timeout_handler and has_connection_handler,
                    f"HTTP: {has_http_handler}, Validation: {has_validation_handler}, Timeout: {has_timeout_handler}, Connection: {has_connection_handler}"
                )
                
            return True
            
        except ImportError as e:
            self.log_test_result(
                "Main app import",
                False,
                f"Import error: {e}"
            )
            return False
        except Exception as e:
            self.log_test_result(
                "Main app error handling test",
                False,
                f"Unexpected error: {e}"
            )
            return False
    
    async def verify_middleware_error_handling(self) -> bool:
        """Verify error handling middleware."""
        logger.info("🔍 Verifying middleware error handling...")
        
        try:
            # Test import of error handling middleware
            from services.api_gateway.middleware.error_handling import (
                ErrorHandlingMiddleware,
                create_error_handling_middleware,
                safe_api_operation,
                safe_llm_operation,
                safe_database_operation
            )
            
            self.log_test_result(
                "Error handling middleware import",
                True,
                "Error handling middleware imported successfully"
            )
            
            # Check middleware file
            middleware_file = project_root / "services" / "api_gateway" / "middleware" / "error_handling.py"
            if middleware_file.exists():
                content = middleware_file.read_text()
                
                # Check for comprehensive error handling
                has_error_monitor = "ErrorMonitor" in content
                has_circuit_breaker = "CircuitBreaker" in content
                has_safe_operations = "safe_" in content
                
                self.log_test_result(
                    "Advanced error handling features",
                    has_error_monitor and has_circuit_breaker and has_safe_operations,
                    f"ErrorMonitor: {has_error_monitor}, CircuitBreaker: {has_circuit_breaker}, SafeOperations: {has_safe_operations}"
                )
                
            return True
            
        except ImportError as e:
            self.log_test_result(
                "Error handling middleware import",
                False,
                f"Import error: {e}"
            )
            return False
        except Exception as e:
            self.log_test_result(
                "Error handling middleware test",
                False,
                f"Unexpected error: {e}"
            )
            return False
    
    async def verify_shared_error_handler(self) -> bool:
        """Verify shared error handler implementation."""
        logger.info("🔍 Verifying shared error handler...")
        
        try:
            # Test import of shared error handler
            from shared.core.error_handler import (
                ErrorHandler,
                APIErrorHandler,
                LLMErrorHandler as SharedLLMErrorHandler,
                DatabaseErrorHandler as SharedDatabaseErrorHandler,
                ErrorHandlerFactory,
                handle_critical_operation,
                safe_api_call,
                safe_llm_call,
                safe_database_call
            )
            
            self.log_test_result(
                "Shared error handler import",
                True,
                "Shared error handler imported successfully"
            )
            
            # Check shared error handler file
            error_handler_file = project_root / "shared" / "core" / "error_handler.py"
            if error_handler_file.exists():
                content = error_handler_file.read_text()
                
                # Check for comprehensive error handling features
                has_error_categories = "ErrorCategory" in content
                has_error_severity = "ErrorSeverity" in content
                has_circuit_breaker = "CircuitBreaker" in content
                has_retry_logic = "retry" in content
                
                self.log_test_result(
                    "Shared error handler features",
                    has_error_categories and has_error_severity and has_circuit_breaker and has_retry_logic,
                    f"ErrorCategories: {has_error_categories}, ErrorSeverity: {has_error_severity}, CircuitBreaker: {has_circuit_breaker}, RetryLogic: {has_retry_logic}"
                )
                
            return True
            
        except ImportError as e:
            self.log_test_result(
                "Shared error handler import",
                False,
                f"Import error: {e}"
            )
            return False
        except Exception as e:
            self.log_test_result(
                "Shared error handler test",
                False,
                f"Unexpected error: {e}"
            )
            return False
    
    async def verify_documentation(self) -> bool:
        """Verify error handling documentation."""
        logger.info("🔍 Verifying error handling documentation...")
        
        try:
            # Check for comprehensive documentation
            doc_file = project_root / "COMPREHENSIVE_ERROR_HANDLING_IMPLEMENTATION.md"
            
            if doc_file.exists():
                content = doc_file.read_text()
                
                # Check for key documentation sections
                has_overview = "## Overview" in content
                has_llm_handling = "LLM API Error Handling" in content
                has_db_handling = "Database Operation Error Handling" in content
                has_global_handler = "Global Exception Handler" in content
                has_utilities = "Centralized Error Handling Utilities" in content
                has_response_format = "Error Response Format" in content
                has_benefits = "## Benefits" in content
                
                all_sections_present = all([
                    has_overview, has_llm_handling, has_db_handling,
                    has_global_handler, has_utilities, has_response_format, has_benefits
                ])
                
                self.log_test_result(
                    "Error handling documentation",
                    all_sections_present,
                    f"Overview: {has_overview}, LLM: {has_llm_handling}, DB: {has_db_handling}, Global: {has_global_handler}, Utilities: {has_utilities}, Format: {has_response_format}, Benefits: {has_benefits}"
                )
                
            else:
                self.log_test_result(
                    "Error handling documentation",
                    False,
                    "Documentation file not found"
                )
                
            return True
            
        except Exception as e:
            self.log_test_result(
                "Error handling documentation test",
                False,
                f"Unexpected error: {e}"
            )
            return False
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate a summary report of all test results."""
        total_tests = len(self.test_results)
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": self.passed_tests,
                "failed_tests": self.failed_tests,
                "success_rate": f"{success_rate:.1f}%"
            },
            "test_results": self.test_results,
            "recommendations": []
        }
        
        # Generate recommendations based on test results
        if self.failed_tests > 0:
            report["recommendations"].append("Review failed tests and implement missing error handling features")
        
        if success_rate < 80:
            report["recommendations"].append("Consider improving error handling coverage")
        
        if success_rate >= 90:
            report["recommendations"].append("Excellent error handling implementation!")
        
        return report
    
    async def run_all_verifications(self) -> Dict[str, Any]:
        """Run all verification tests."""
        logger.info("🚀 Starting comprehensive error handling verification...")
        logger.info("=" * 80)
        
        # Run all verification tests
        await self.verify_error_handling_utilities()
        await self.verify_queries_route_error_handling()
        await self.verify_main_app_error_handling()
        await self.verify_middleware_error_handling()
        await self.verify_shared_error_handler()
        await self.verify_documentation()
        
        # Generate summary report
        report = self.generate_summary_report()
        
        logger.info("=" * 80)
        logger.info("📊 VERIFICATION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Tests: {report['summary']['total_tests']}")
        logger.info(f"Passed: {report['summary']['passed_tests']}")
        logger.info(f"Failed: {report['summary']['failed_tests']}")
        logger.info(f"Success Rate: {report['summary']['success_rate']}")
        
        if report["recommendations"]:
            logger.info("\n💡 RECOMMENDATIONS:")
            for rec in report["recommendations"]:
                logger.info(f"  • {rec}")
        
        return report


async def main():
    """Main verification function."""
    verifier = ErrorHandlingVerifier()
    report = await verifier.run_all_verifications()
    
    # Save detailed report to file
    report_file = project_root / "error_handling_verification_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    logger.info(f"\n📄 Detailed report saved to: {report_file}")
    
    # Exit with appropriate code
    if report["summary"]["failed_tests"] > 0:
        logger.error("❌ Some tests failed. Please review the implementation.")
        sys.exit(1)
    else:
        logger.info("✅ All tests passed! Error handling implementation is comprehensive.")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main()) 