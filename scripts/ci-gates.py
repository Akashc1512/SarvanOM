#!/usr/bin/env python3
"""
CI Gates CLI Script - SarvanOM v2

Command-line interface for running CI quality gates locally.
Implements PR-6 CI hardening requirements for local validation.
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import Optional

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sarvanom.shared.ci.ci_gates import CIGatesService, CIGateReport
from sarvanom.shared.ci.provider_key_validator import get_provider_key_validator
from sarvanom.shared.observability.fallback_metrics import get_fallback_metrics

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Run CI quality gates for SarvanOM v2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all gates
  python scripts/ci-gates.py

  # Run only provider key validation
  python scripts/ci-gates.py --gates provider-keys

  # Export report to file
  python scripts/ci-gates.py --output report.json

  # Check specific lane
  python scripts/ci-gates.py --lane web_search

  # Validate with keyless fallbacks disabled
  python scripts/ci-gates.py --disable-keyless-fallbacks
        """
    )
    
    parser.add_argument(
        "--gates",
        choices=["all", "provider-keys", "budget-compliance", "keyless-fallbacks", "performance"],
        default="all",
        help="Which gates to run (default: all)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Output file for detailed report (JSON format)"
    )
    
    parser.add_argument(
        "--format",
        choices=["text", "json", "summary"],
        default="text",
        help="Output format (default: text)"
    )
    
    parser.add_argument(
        "--lane",
        type=str,
        help="Check specific lane only"
    )
    
    parser.add_argument(
        "--disable-keyless-fallbacks",
        action="store_true",
        help="Disable keyless fallbacks for validation"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--exit-on-failure",
        action="store_true",
        default=True,
        help="Exit with non-zero code on failure (default: True)"
    )
    
    args = parser.parse_args()
    
    try:
        # Set environment variables
        if args.disable_keyless_fallbacks:
            os.environ["KEYLESS_FALLBACKS_ENABLED"] = "false"
        else:
            os.environ["KEYLESS_FALLBACKS_ENABLED"] = "true"
        
        # Run gates
        if args.gates == "all":
            service = CIGatesService()
            report = service.run_all_gates()
        else:
            report = run_specific_gates(args.gates, args.lane, args.verbose)
        
        # Output results
        if args.format == "json":
            output = service.export_report(report, "json")
        elif args.format == "summary":
            output = report.summary
        else:
            output = format_text_report(report, args.verbose)
        
        print(output)
        
        # Save to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                if args.format == "json":
                    f.write(service.export_report(report, "json"))
                else:
                    f.write(output)
            print(f"\nReport saved to: {args.output}")
        
        # Exit with appropriate code
        if args.exit_on_failure and not report.overall_passed:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def run_specific_gates(gate_type: str, lane: Optional[str], verbose: bool) -> CIGateReport:
    """Run specific gates"""
    service = CIGatesService()
    
    if gate_type == "provider-keys":
        gates = service._run_provider_key_gates()
    elif gate_type == "budget-compliance":
        gates = service._run_budget_compliance_gates()
    elif gate_type == "keyless-fallbacks":
        gates = service._run_keyless_fallback_gates()
    elif gate_type == "performance":
        gates = service._run_performance_gates()
    else:
        raise ValueError(f"Unknown gate type: {gate_type}")
    
    # Filter by lane if specified
    if lane:
        gates = [gate for gate in gates if lane in gate.gate_name]
    
    # Create report
    overall_passed = all(gate.passed for gate in gates)
    summary = service._generate_summary(gates, overall_passed)
    
    return CIGateReport(
        overall_passed=overall_passed,
        gates=gates,
        summary=summary,
        timestamp=service.metrics.events[-1].timestamp if service.metrics.events else None,
        environment=service.environment
    )

def format_text_report(report: CIGateReport, verbose: bool) -> str:
    """Format report as text"""
    output = []
    
    # Header
    status_emoji = "✅" if report.overall_passed else "❌"
    output.append(f"{status_emoji} CI Gates Report")
    output.append("=" * 50)
    output.append(f"Environment: {report.environment}")
    output.append(f"Timestamp: {report.timestamp}")
    output.append(f"Overall Status: {'PASSED' if report.overall_passed else 'FAILED'}")
    output.append("")
    
    # Gate results
    output.append("Gate Results:")
    output.append("-" * 20)
    
    for gate in report.gates:
        status_emoji = "✅" if gate.passed else "❌"
        severity_emoji = {
            "error": "🔴",
            "warning": "🟡",
            "info": "🔵"
        }.get(gate.severity, "⚪")
        
        output.append(f"{status_emoji} {severity_emoji} {gate.gate_name}")
        output.append(f"   {gate.message}")
        
        if verbose and gate.details:
            output.append("   Details:")
            for key, value in gate.details.items():
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, indent=6)
                output.append(f"     {key}: {value}")
        output.append("")
    
    # Summary
    output.append("Summary:")
    output.append("-" * 10)
    output.append(report.summary)
    
    return "\n".join(output)

if __name__ == "__main__":
    main()
