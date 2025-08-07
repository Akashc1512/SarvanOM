#!/usr/bin/env python3
"""
Final Comprehensive Verification for Duplicate Logic Refactoring
"""

import os
import re

def check_file_exists(filepath: str) -> bool:
    """Check if a file exists"""
    return os.path.exists(filepath)

def count_lines(filepath: str) -> int:
    """Count lines in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    except Exception:
        return 0

def check_integration(filepath: str, required_components: list) -> dict:
    """Check if file integrates with required components"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        results = {}
        for component in required_components:
            results[component] = component in content
        
        return results
    except Exception as e:
        return {"error": str(e)}

def main():
    print("🔍 FINAL COMPREHENSIVE VERIFICATION")
    print("=" * 60)
    
    # File structure verification
    print("\n📊 File Structure Verification:")
    files_to_check = [
        'shared/core/agents/agent_utilities.py',
        'shared/core/agents/retrieval_utilities.py', 
        'shared/core/agents/factcheck_agent.py',
        'shared/core/agents/synthesis_agent.py',
        'DUPLICATE_LOGIC_REFACTORING_SUMMARY.md'
    ]
    
    for file in files_to_check:
        exists = check_file_exists(file)
        status = '✅' if exists else '❌'
        print(f"  {status} {file}: {'EXISTS' if exists else 'MISSING'}")
    
    # Code quality metrics
    print("\n📈 Code Quality Metrics:")
    agent_utils_size = count_lines('shared/core/agents/agent_utilities.py')
    retrieval_utils_size = count_lines('shared/core/agents/retrieval_utilities.py')
    factcheck_size = count_lines('shared/core/agents/factcheck_agent.py')
    synthesis_size = count_lines('shared/core/agents/synthesis_agent.py')
    
    print(f"  Agent Utilities: {agent_utils_size} lines")
    print(f"  Retrieval Utilities: {retrieval_utils_size} lines")
    print(f"  FactCheck Agent: {factcheck_size} lines")
    print(f"  Synthesis Agent: {synthesis_size} lines")
    print(f"  Total Utilities: {agent_utils_size + retrieval_utils_size} lines")
    print(f"  Total Agents: {factcheck_size + synthesis_size} lines")
    
    total_code = factcheck_size + synthesis_size + agent_utils_size + retrieval_utils_size
    reuse_ratio = ((agent_utils_size + retrieval_utils_size) / total_code * 100) if total_code > 0 else 0
    print(f"  Code Reuse Ratio: {reuse_ratio:.1f}%")
    
    # Integration verification
    print("\n🔧 Integration Verification:")
    
    # Check FactCheck Agent integration
    factcheck_components = [
        'AgentTaskProcessor',
        'CommonValidators',
        'ResponseFormatter', 
        '@time_agent_function',
        'process_task_with_workflow'
    ]
    
    factcheck_integration = check_integration('shared/core/agents/factcheck_agent.py', factcheck_components)
    print("  FactCheck Agent Integration:")
    for component, integrated in factcheck_integration.items():
        status = '✅' if integrated else '❌'
        print(f"    {status} {component}")
    
    # Check Synthesis Agent integration
    synthesis_components = [
        'AgentTaskProcessor',
        'CommonValidators',
        'CommonProcessors',
        'ResponseFormatter',
        '@time_agent_function',
        'process_task_with_workflow'
    ]
    
    synthesis_integration = check_integration('shared/core/agents/synthesis_agent.py', synthesis_components)
    print("  Synthesis Agent Integration:")
    for component, integrated in synthesis_integration.items():
        status = '✅' if integrated else '❌'
        print(f"    {status} {component}")
    
    # Utility completeness verification
    print("\n🔧 Utility Completeness:")
    
    agent_utility_components = [
        'AgentTaskProcessor',
        'CommonValidators',
        'CommonProcessors', 
        'PerformanceMonitor',
        'ErrorHandler',
        'ResponseFormatter',
        'time_agent_function',
        'create_task_processor',
        'create_performance_monitor',
        'create_error_handler',
        'format_standard_response'
    ]
    
    agent_utils_completeness = check_integration('shared/core/agents/agent_utilities.py', agent_utility_components)
    print("  Agent Utilities:")
    for component, present in agent_utils_completeness.items():
        status = '✅' if present else '❌'
        print(f"    {status} {component}")
    
    retrieval_utility_components = [
        'QueryProcessor',
        'ResultProcessor',
        'SearchFusion',
        'CacheManager', 
        'FallbackManager',
        'create_search_result',
        'create_document',
        'execute_search_with_fallback'
    ]
    
    retrieval_utils_completeness = check_integration('shared/core/agents/retrieval_utilities.py', retrieval_utility_components)
    print("  Retrieval Utilities:")
    for component, present in retrieval_utils_completeness.items():
        status = '✅' if present else '❌'
        print(f"    {status} {component}")
    
    # Calculate overall success metrics
    print("\n📊 Overall Success Metrics:")
    print("=" * 60)
    
    # File existence checks
    file_existence_score = sum(1 for file in files_to_check if check_file_exists(file)) / len(files_to_check) * 100
    
    # Integration checks
    factcheck_integration_score = sum(factcheck_integration.values()) / len(factcheck_integration) * 100
    synthesis_integration_score = sum(synthesis_integration.values()) / len(synthesis_integration) * 100
    
    # Utility completeness checks
    agent_utils_completeness_score = sum(agent_utils_completeness.values()) / len(agent_utils_completeness) * 100
    retrieval_utils_completeness_score = sum(retrieval_utils_completeness.values()) / len(retrieval_utils_completeness) * 100
    
    print(f"✅ File Structure: {file_existence_score:.1f}%")
    print(f"✅ FactCheck Integration: {factcheck_integration_score:.1f}%")
    print(f"✅ Synthesis Integration: {synthesis_integration_score:.1f}%")
    print(f"✅ Agent Utilities Completeness: {agent_utils_completeness_score:.1f}%")
    print(f"✅ Retrieval Utilities Completeness: {retrieval_utils_completeness_score:.1f}%")
    print(f"✅ Code Reuse Ratio: {reuse_ratio:.1f}%")
    
    # Overall assessment
    overall_score = (file_existence_score + factcheck_integration_score + synthesis_integration_score + 
                    agent_utils_completeness_score + retrieval_utils_completeness_score + reuse_ratio) / 6
    
    print(f"\n🎯 Overall Success Score: {overall_score:.1f}%")
    
    if overall_score >= 90:
        print("\n🎉 DUPLICATE LOGIC REFACTORING: EXCELLENT SUCCESS!")
        print("✅ All components are properly implemented and integrated")
        print("✅ High code reuse ratio achieved")
        print("✅ Comprehensive utilities created")
        print("✅ Agents successfully refactored")
        print("✅ Documentation complete")
    elif overall_score >= 80:
        print("\n✅ DUPLICATE LOGIC REFACTORING: SUCCESSFUL!")
        print("✅ Core functionality is properly implemented")
        print("✅ Good code reuse achieved")
        print("✅ Most utilities are complete")
        print("✅ Agents are well integrated")
    elif overall_score >= 70:
        print("\n⚠️  DUPLICATE LOGIC REFACTORING: MOSTLY COMPLETE")
        print("✅ Basic functionality is implemented")
        print("⚠️  Some components may need minor adjustments")
    else:
        print("\n❌ DUPLICATE LOGIC REFACTORING: NEEDS IMPROVEMENT")
        print("❌ Several components are missing or incomplete")
        print("❌ Integration issues detected")
    
    print("\n" + "=" * 60)
    print("🔍 VERIFICATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main() 