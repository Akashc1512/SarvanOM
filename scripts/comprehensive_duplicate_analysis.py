#!/usr/bin/env python3
"""
Comprehensive Duplicate Logic Analysis

This script scans the backend code for duplicate or very similar logic blocks,
especially in agent and retrieval workflows, and creates a detailed report.
"""

import os
import re
import ast
import asyncio
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@dataclass
class DuplicatePattern:
    """Represents a duplicate pattern found in the codebase."""
    pattern_name: str
    pattern_type: str
    files: List[str] = field(default_factory=list)
    line_numbers: List[List[int]] = field(default_factory=list)
    code_snippets: List[str] = field(default_factory=list)
    similarity_score: float = 0.0
    suggested_utility: str = ""

@dataclass
class AnalysisResult:
    """Results of the duplicate analysis."""
    total_patterns: int = 0
    duplicate_patterns: List[DuplicatePattern] = field(default_factory=list)
    files_analyzed: List[str] = field(default_factory=list)
    total_duplicate_lines: int = 0

class DuplicateAnalyzer:
    """Analyzes code for duplicate patterns."""
    
    def __init__(self):
        self.patterns = []
        self.results = AnalysisResult()
        
    def analyze_backend_code(self) -> AnalysisResult:
        """Analyze the entire backend codebase for duplicates."""
        print("🔍 Starting comprehensive duplicate analysis...")
        
        # Define directories to analyze
        backend_dirs = [
            "shared/core/agents",
            "services/api_gateway",
            "shared/core/services",
            "shared/core/llm_client_v3.py",
            "shared/core/config",
            "shared/core/error_handler.py"
        ]
        
        for directory in backend_dirs:
            if os.path.exists(directory):
                self._analyze_directory(directory)
        
        return self.results
    
    def _analyze_directory(self, directory: str):
        """Analyze a directory for duplicate patterns."""
        print(f"📁 Analyzing directory: {directory}")
        
        if os.path.isfile(directory):
            self._analyze_file(directory)
        else:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        self._analyze_file(file_path)
    
    def _analyze_file(self, file_path: str):
        """Analyze a single file for duplicate patterns."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.results.files_analyzed.append(file_path)
            
            # Analyze for specific patterns
            self._find_timing_patterns(content, file_path)
            self._find_error_handling_patterns(content, file_path)
            self._find_validation_patterns(content, file_path)
            self._find_agent_workflow_patterns(content, file_path)
            self._find_retrieval_patterns(content, file_path)
            self._find_logging_patterns(content, file_path)
            self._find_response_formatting_patterns(content, file_path)
            
        except Exception as e:
            print(f"⚠️ Error analyzing {file_path}: {e}")
    
    def _find_timing_patterns(self, content: str, file_path: str):
        """Find timing-related duplicate patterns."""
        patterns = [
            (r'start_time\s*=\s*time\.time\(\)', "Timing Start"),
            (r'execution_time\s*=\s*\(time\.time\(\)\s*-\s*start_time\)\s*\*\s*1000', "Timing Calculation"),
            (r'processing_time\s*=\s*int\(\(time\.time\(\)\s*-\s*start_time\)\s*\*\s*1000\)', "Processing Time"),
        ]
        
        for pattern, pattern_name in patterns:
            matches = re.finditer(pattern, content)
            if len(list(matches)) > 1:  # More than one occurrence
                self._add_pattern(file_path, pattern_name, "Timing", pattern)
    
    def _find_error_handling_patterns(self, content: str, file_path: str):
        """Find error handling duplicate patterns."""
        patterns = [
            (r'try:\s*\n(.*?)\nexcept\s+Exception\s+as\s+e:', "Try-Except Block"),
            (r'return\s*\{\s*["\']success["\']\s*:\s*False\s*,\s*["\']error["\']\s*:\s*str\(e\)\s*\}', "Error Response"),
            (r'logger\.error\(f["\'][^"\']*["\']\s*,\s*error_type=type\(e\)\.__name__', "Error Logging"),
        ]
        
        for pattern, pattern_name in patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            if len(list(matches)) > 1:
                self._add_pattern(file_path, pattern_name, "Error Handling", pattern)
    
    def _find_validation_patterns(self, content: str, file_path: str):
        """Find validation duplicate patterns."""
        patterns = [
            (r'if\s+not\s+\w+\s+or\s+not\s+isinstance\(\w+,\s*str\):', "String Validation"),
            (r'if\s+len\(\w+\.strip\(\)\)\s*==\s*0:', "Empty String Check"),
            (r'if\s+len\(\w+\)\s*>\s*\d+:', "Length Validation"),
            (r'missing_fields\s*=\s*\[\]', "Required Fields Check"),
        ]
        
        for pattern, pattern_name in patterns:
            matches = re.finditer(pattern, content)
            if len(list(matches)) > 1:
                self._add_pattern(file_path, pattern_name, "Validation", pattern)
    
    def _find_agent_workflow_patterns(self, content: str, file_path: str):
        """Find agent workflow duplicate patterns."""
        patterns = [
            (r'async\s+def\s+process_task\(self,\s*task:\s*Dict\[str,\s*Any\],\s*context:', "Agent Process Task"),
            (r'result\s*=\s*await\s+self\.task_processor\.process_task_with_workflow', "Task Processor Usage"),
            (r'return\s+ResponseFormatter\.format_agent_response', "Response Formatting"),
        ]
        
        for pattern, pattern_name in patterns:
            matches = re.finditer(pattern, content)
            if len(list(matches)) > 1:
                self._add_pattern(file_path, pattern_name, "Agent Workflow", pattern)
    
    def _find_retrieval_patterns(self, content: str, file_path: str):
        """Find retrieval duplicate patterns."""
        patterns = [
            (r'async\s+def\s+\w+_search\(self,\s*query:\s*str', "Search Method"),
            (r'documents\s*=\s*\[\]', "Document List Initialization"),
            (r'for\s+doc\s+in\s+documents:', "Document Processing Loop"),
            (r'result\s*=\s*SearchResult\(', "Search Result Creation"),
        ]
        
        for pattern, pattern_name in patterns:
            matches = re.finditer(pattern, content)
            if len(list(matches)) > 1:
                self._add_pattern(file_path, pattern_name, "Retrieval", pattern)
    
    def _find_logging_patterns(self, content: str, file_path: str):
        """Find logging duplicate patterns."""
        patterns = [
            (r'logger\.info\(f["\'][^"\']*["\']\s*,\s*\*\*kwargs\)', "Info Logging"),
            (r'logger\.error\(f["\'][^"\']*["\']\s*,\s*error_type=type\(e\)\.__name__', "Error Logging"),
            (r'logger\.warning\(f["\'][^"\']*["\']', "Warning Logging"),
        ]
        
        for pattern, pattern_name in patterns:
            matches = re.finditer(pattern, content)
            if len(list(matches)) > 1:
                self._add_pattern(file_path, pattern_name, "Logging", pattern)
    
    def _find_response_formatting_patterns(self, content: str, file_path: str):
        """Find response formatting duplicate patterns."""
        patterns = [
            (r'return\s*\{\s*["\']success["\']\s*:\s*True', "Success Response"),
            (r'return\s*\{\s*["\']success["\']\s*:\s*False', "Error Response"),
            (r'["\']confidence["\']\s*:\s*\d+\.\d+', "Confidence Field"),
            (r'["\']execution_time_ms["\']\s*:\s*\w+', "Execution Time Field"),
        ]
        
        for pattern, pattern_name in patterns:
            matches = re.finditer(pattern, content)
            if len(list(matches)) > 1:
                self._add_pattern(file_path, pattern_name, "Response Formatting", pattern)
    
    def _add_pattern(self, file_path: str, pattern_name: str, pattern_type: str, regex_pattern: str):
        """Add a duplicate pattern to the results."""
        # Check if this pattern already exists
        existing_pattern = None
        for pattern in self.results.duplicate_patterns:
            if pattern.pattern_name == pattern_name and pattern.pattern_type == pattern_type:
                existing_pattern = pattern
                break
        
        if existing_pattern:
            if file_path not in existing_pattern.files:
                existing_pattern.files.append(file_path)
        else:
            new_pattern = DuplicatePattern(
                pattern_name=pattern_name,
                pattern_type=pattern_type,
                files=[file_path],
                suggested_utility=self._suggest_utility(pattern_name, pattern_type)
            )
            self.results.duplicate_patterns.append(new_pattern)
    
    def _suggest_utility(self, pattern_name: str, pattern_type: str) -> str:
        """Suggest a utility function for the pattern."""
        suggestions = {
            "Timing": {
                "Timing Start": "timing_utilities.start_timer()",
                "Timing Calculation": "timing_utilities.calculate_execution_time()",
                "Processing Time": "timing_utilities.get_processing_time()"
            },
            "Error Handling": {
                "Try-Except Block": "error_utilities.safe_execute()",
                "Error Response": "error_utilities.create_error_response()",
                "Error Logging": "error_utilities.log_error()"
            },
            "Validation": {
                "String Validation": "validation_utilities.validate_string()",
                "Empty String Check": "validation_utilities.validate_non_empty()",
                "Length Validation": "validation_utilities.validate_length()",
                "Required Fields Check": "validation_utilities.validate_required_fields()"
            },
            "Agent Workflow": {
                "Agent Process Task": "agent_utilities.standard_process_task()",
                "Task Processor Usage": "agent_utilities.process_with_workflow()",
                "Response Formatting": "agent_utilities.format_agent_response()"
            },
            "Retrieval": {
                "Search Method": "retrieval_utilities.standard_search()",
                "Document List Initialization": "retrieval_utilities.create_document_list()",
                "Document Processing Loop": "retrieval_utilities.process_documents()",
                "Search Result Creation": "retrieval_utilities.create_search_result()"
            },
            "Logging": {
                "Info Logging": "logging_utilities.log_info()",
                "Error Logging": "logging_utilities.log_error()",
                "Warning Logging": "logging_utilities.log_warning()"
            },
            "Response Formatting": {
                "Success Response": "response_utilities.create_success_response()",
                "Error Response": "response_utilities.create_error_response()",
                "Confidence Field": "response_utilities.add_confidence()",
                "Execution Time Field": "response_utilities.add_execution_time()"
            }
        }
        
        return suggestions.get(pattern_type, {}).get(pattern_name, "custom_utility()")
    
    def generate_report(self) -> str:
        """Generate a comprehensive report of duplicate patterns."""
        report = []
        report.append("# COMPREHENSIVE DUPLICATE LOGIC ANALYSIS REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Summary
        report.append(f"## 📊 SUMMARY")
        report.append(f"- **Total Files Analyzed**: {len(self.results.files_analyzed)}")
        report.append(f"- **Duplicate Patterns Found**: {len(self.results.duplicate_patterns)}")
        report.append(f"- **Pattern Types**: {len(set(p.pattern_type for p in self.results.duplicate_patterns))}")
        report.append("")
        
        # Group by pattern type
        by_type = {}
        for pattern in self.results.duplicate_patterns:
            if pattern.pattern_type not in by_type:
                by_type[pattern.pattern_type] = []
            by_type[pattern.pattern_type].append(pattern)
        
        for pattern_type, patterns in by_type.items():
            report.append(f"## 🔍 {pattern_type.upper()} PATTERNS")
            report.append("")
            
            for pattern in patterns:
                report.append(f"### {pattern.pattern_name}")
                report.append(f"- **Files**: {', '.join(pattern.files)}")
                report.append(f"- **Suggested Utility**: `{pattern.suggested_utility}`")
                report.append("")
        
        # Recommendations
        report.append("## 🎯 RECOMMENDATIONS")
        report.append("")
        report.append("### 1. Create Shared Utilities")
        report.append("- Extract common patterns to reusable modules")
        report.append("- Maintain all original functionality")
        report.append("- Use utilities in existing code")
        report.append("")
        
        report.append("### 2. Priority Patterns to Extract")
        priority_patterns = [
            "Agent Process Task",
            "Try-Except Block", 
            "Timing Start",
            "Response Formatting",
            "Error Response"
        ]
        
        for pattern_name in priority_patterns:
            for pattern in self.results.duplicate_patterns:
                if pattern.pattern_name == pattern_name:
                    report.append(f"- **{pattern_name}**: Found in {len(pattern.files)} files")
                    break
        
        report.append("")
        report.append("### 3. Implementation Strategy")
        report.append("1. Create utility modules for each pattern type")
        report.append("2. Update existing code to use utilities")
        report.append("3. Preserve all original functionality")
        report.append("4. Test thoroughly to ensure nothing breaks")
        
        return "\n".join(report)

def main():
    """Main analysis function."""
    print("🔍 Starting comprehensive duplicate logic analysis...")
    
    analyzer = DuplicateAnalyzer()
    results = analyzer.analyze_backend_code()
    
    # Generate and save report
    report = analyzer.generate_report()
    
    with open("COMPREHENSIVE_DUPLICATE_ANALYSIS_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("✅ Analysis complete!")
    print(f"📊 Found {len(results.duplicate_patterns)} duplicate patterns")
    print(f"📁 Analyzed {len(results.files_analyzed)} files")
    print("📄 Report saved to: COMPREHENSIVE_DUPLICATE_ANALYSIS_REPORT.md")
    
    # Print summary
    print("\n🎯 KEY FINDINGS:")
    by_type = {}
    for pattern in results.duplicate_patterns:
        if pattern.pattern_type not in by_type:
            by_type[pattern.pattern_type] = 0
        by_type[pattern.pattern_type] += 1
    
    for pattern_type, count in by_type.items():
        print(f"  - {pattern_type}: {count} patterns")
    
    print("\n📋 NEXT STEPS:")
    print("1. Review the detailed report")
    print("2. Create shared utility modules")
    print("3. Refactor existing code to use utilities")
    print("4. Preserve all original functionality")

if __name__ == "__main__":
    main() 