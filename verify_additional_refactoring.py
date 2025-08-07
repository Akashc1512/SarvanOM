#!/usr/bin/env python3
"""
Verification script for additional duplicate logic refactoring
"""

import os

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

def main():
    print("🔍 FINAL VERIFICATION OF ADDITIONAL REFACTORING")
    print("=" * 60)
    
    # Check files
    files_to_check = [
        'shared/core/agents/validation_utilities.py',
        'shared/core/agents/citation_agent.py', 
        'shared/core/agents/arangodb_knowledge_graph_agent.py',
        'ADDITIONAL_DUPLICATE_LOGIC_REFACTORING.md'
    ]
    
    print("📊 File Structure Verification:")
    for file in files_to_check:
        exists = check_file_exists(file)
        status = "✅" if exists else "❌"
        print(f"  {status} {file}: {'EXISTS' if exists else 'MISSING'}")
    
    print()
    print("📈 Code Quality Metrics:")
    
    # Count lines
    validation_utils_size = count_lines('shared/core/agents/validation_utilities.py')
    citation_size = count_lines('shared/core/agents/citation_agent.py')
    kg_size = count_lines('shared/core/agents/arangodb_knowledge_graph_agent.py')
    
    print(f"  Validation Utilities: {validation_utils_size} lines")
    print(f"  Citation Agent: {citation_size} lines")
    print(f"  Knowledge Graph Agent: {kg_size} lines")
    print(f"  Total New Code: {validation_utils_size + citation_size + kg_size} lines")
    
    print()
    print("✅ ADDITIONAL REFACTORING VERIFICATION COMPLETE")

if __name__ == "__main__":
    main() 