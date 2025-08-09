#!/usr/bin/env python3
"""
Analyze the improvements achieved through duplicate logic refactoring
"""

import os
import re


def count_lines_in_method(filepath: str, method_name: str) -> int:
    """Count lines in a specific method"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Find method start
        method_pattern = rf"async def {method_name}\s*\([^)]*\)[^:]*:"
        match = re.search(method_pattern, content)
        if not match:
            return 0

        start_pos = match.start()

        # Find method end (next method or class)
        lines = content[start_pos:].split("\n")
        method_lines = []
        indent_level = None

        for i, line in enumerate(lines):
            if i == 0:  # First line is the method definition
                method_lines.append(line)
                # Calculate indent level
                indent_level = len(line) - len(line.lstrip())
                continue

            # Check if we've reached the end of the method
            if (
                line.strip()
                and not line.startswith(" " * (indent_level + 1))
                and not line.startswith("\t")
            ):
                # Check if it's a new method or class definition
                if re.match(r"^(async def|def|class)\s+", line.strip()):
                    break

            method_lines.append(line)

        return len([line for line in method_lines if line.strip()])

    except Exception as e:
        print(f"Error analyzing {filepath}: {e}")
        return 0


def analyze_agent_complexity():
    """Analyze the complexity reduction in refactored agents"""
    print("🔍 ANALYZING REFACTORING IMPROVEMENTS")
    print("=" * 60)

    # Analyze FactCheck Agent
    print("\n📊 FactCheck Agent Analysis:")
    factcheck_process_task_lines = count_lines_in_method(
        "shared/core/agents/factcheck_agent.py", "process_task"
    )
    print(f"  process_task method: {factcheck_process_task_lines} lines")

    # Analyze Synthesis Agent
    print("\n📊 Synthesis Agent Analysis:")
    synthesis_process_task_lines = count_lines_in_method(
        "shared/core/agents/synthesis_agent.py", "process_task"
    )
    print(f"  process_task method: {synthesis_process_task_lines} lines")

    # Analyze utility files
    print("\n📊 Utility Files Analysis:")
    agent_utils_lines = len(
        open("shared/core/agents/agent_utilities.py", "r", encoding="utf-8").readlines()
    )
    retrieval_utils_lines = len(
        open(
            "shared/core/agents/retrieval_utilities.py", "r", encoding="utf-8"
        ).readlines()
    )
    print(f"  Agent Utilities: {agent_utils_lines} lines")
    print(f"  Retrieval Utilities: {retrieval_utils_lines} lines")
    print(f"  Total Utilities: {agent_utils_lines + retrieval_utils_lines} lines")

    # Calculate improvements
    total_agent_method_lines = (
        factcheck_process_task_lines + synthesis_process_task_lines
    )
    total_utility_lines = agent_utils_lines + retrieval_utils_lines

    print("\n📈 IMPROVEMENT METRICS:")
    print("=" * 60)
    print(f"✅ Simplified agent methods: {total_agent_method_lines} lines total")
    print(f"✅ Reusable utilities created: {total_utility_lines} lines")
    print(
        f"✅ Code reuse ratio: {(total_utility_lines / (total_agent_method_lines + total_utility_lines) * 100):.1f}%"
    )

    # Check for specific improvements
    print("\n🔧 SPECIFIC IMPROVEMENTS:")
    print("=" * 60)

    # Check FactCheck Agent for improvements
    with open("shared/core/agents/factcheck_agent.py", "r", encoding="utf-8") as f:
        factcheck_content = f.read()

    improvements = []
    if "AgentTaskProcessor" in factcheck_content:
        improvements.append("✅ Uses AgentTaskProcessor for standardized workflow")
    if "CommonValidators" in factcheck_content:
        improvements.append("✅ Uses CommonValidators for input validation")
    if "ResponseFormatter" in factcheck_content:
        improvements.append("✅ Uses ResponseFormatter for consistent output")
    if "@time_agent_function" in factcheck_content:
        improvements.append("✅ Uses performance monitoring decorator")
    if "process_task_with_workflow" in factcheck_content:
        improvements.append("✅ Uses standardized workflow processing")

    for improvement in improvements:
        print(f"  {improvement}")

    # Check Synthesis Agent for improvements
    with open("shared/core/agents/synthesis_agent.py", "r", encoding="utf-8") as f:
        synthesis_content = f.read()

    synthesis_improvements = []
    if "AgentTaskProcessor" in synthesis_content:
        synthesis_improvements.append(
            "✅ Uses AgentTaskProcessor for standardized workflow"
        )
    if "CommonValidators" in synthesis_content:
        synthesis_improvements.append("✅ Uses CommonValidators for input validation")
    if "CommonProcessors" in synthesis_content:
        synthesis_improvements.append("✅ Uses CommonProcessors for data processing")
    if "ResponseFormatter" in synthesis_content:
        synthesis_improvements.append("✅ Uses ResponseFormatter for consistent output")
    if "@time_agent_function" in synthesis_content:
        synthesis_improvements.append("✅ Uses performance monitoring decorator")

    print(f"\n📊 Synthesis Agent Improvements:")
    for improvement in synthesis_improvements:
        print(f"  {improvement}")

    # Check utility completeness
    print(f"\n🔧 Utility Completeness:")
    print("=" * 60)

    with open("shared/core/agents/agent_utilities.py", "r", encoding="utf-8") as f:
        agent_utils_content = f.read()

    utility_features = [
        "AgentTaskProcessor",
        "CommonValidators",
        "CommonProcessors",
        "PerformanceMonitor",
        "ErrorHandler",
        "ResponseFormatter",
        "time_agent_function",
        "create_task_processor",
        "create_performance_monitor",
        "create_error_handler",
        "format_standard_response",
    ]

    for feature in utility_features:
        if feature in agent_utils_content:
            print(f"  ✅ {feature}")
        else:
            print(f"  ❌ {feature}")

    # Check retrieval utilities
    with open("shared/core/agents/retrieval_utilities.py", "r", encoding="utf-8") as f:
        retrieval_utils_content = f.read()

    retrieval_features = [
        "QueryProcessor",
        "ResultProcessor",
        "SearchFusion",
        "CacheManager",
        "FallbackManager",
        "create_search_result",
        "create_document",
        "execute_search_with_fallback",
    ]

    print(f"\n🔍 Retrieval Utilities:")
    for feature in retrieval_features:
        if feature in retrieval_utils_content:
            print(f"  ✅ {feature}")
        else:
            print(f"  ❌ {feature}")

    print("\n" + "=" * 60)
    print("🎉 REFACTORING ANALYSIS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    analyze_agent_complexity()
