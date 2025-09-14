#!/usr/bin/env python3
"""
Simple Component Scanner

A lightweight component scanner for React components that generates
basic provenance data without complex analysis.
"""

import os
import re
import csv
from pathlib import Path
from datetime import datetime

def scan_components():
    """Scan for React components and generate basic analysis"""
    print("Starting component scan...")
    
    frontend_path = Path("frontend")
    src_path = frontend_path / "src"
    
    if not src_path.exists():
        print(f"Frontend src path not found: {src_path}")
        return
    
    print(f"Scanning: {src_path}")
    
    # Find all .tsx and .jsx files
    component_files = []
    for pattern in ["**/*.tsx", "**/*.jsx"]:
        component_files.extend(src_path.glob(pattern))
    
    print(f"Found {len(component_files)} component files")
    
    components = []
    for file_path in component_files:
        # Skip test files and stories
        if any(skip in str(file_path) for skip in ['.test.', '.spec.', '.stories.']):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract component name
            component_name = file_path.stem
            
            # Look for export patterns
            display_name = component_name
            export_patterns = [
                r'export\s+default\s+(\w+)',
                r'export\s+const\s+(\w+)\s*=',
                r'export\s+function\s+(\w+)',
                r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>'
            ]
            
            for pattern in export_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    display_name = matches[0]
                    break
            
            # Check for props interface
            props_signature = "no_props"
            interface_pattern = r'interface\s+(\w+Props)\s*\{([^}]+)\}'
            interface_matches = re.findall(interface_pattern, content, re.DOTALL)
            
            if interface_matches:
                interface_name, props_content = interface_matches[0]
                props_signature = re.sub(r'\s+', ' ', props_content.strip())
            
            # Check for design tokens and accessibility
            tokens_compliant = any(token in content for token in ['design-tokens', 'tokens', 'theme', 'designTokens', '--', 'var('])
            a11y_notes_present = any(a11y in content for a11y in ['aria-', 'role=', 'tabIndex', 'accessibility', 'screen reader', 'keyboard navigation', 'focus management', 'ARIA', 'a11y'])
            
            # Check if component matches contracts (simplified check)
            matches_contract = display_name in ['AppLayout', 'DashboardLayout', 'AuthLayout', 'Navigation', 'Sidebar', 'Breadcrumbs', 'Input', 'Textarea', 'Select', 'Button', 'Table', 'List', 'Card', 'Modal', 'Dialog', 'Alert', 'Toast', 'Progress', 'QueryInput', 'QueryResults', 'KnowledgeGraph', 'AgentCard', 'DatabaseAgent', 'BrowserAgent', 'Container', 'Grid', 'Text']
            
            component_info = {
                'name': component_name,
                'display_name': display_name,
                'path': str(file_path.relative_to(frontend_path)),
                'props_signature': props_signature,
                'file_size': len(content.encode('utf-8')),
                'lines_of_code': len(content.splitlines()),
                'matches_contract': str(matches_contract).lower(),
                'tokens_compliant': str(tokens_compliant).lower(),
                'a11y_notes_present': str(a11y_notes_present).lower(),
                'usage_count': 0,  # Will be calculated later
                'last_commit_date': 'unknown',  # Would need git integration
                'first_commit_date': 'unknown',
                'story_exists': 'false',  # Would need to check for .stories files
                'props_signature_hash': 'unknown'
            }
            
            components.append(component_info)
            print(f"  - {display_name} ({component_info['path']})")
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    print(f"\nFound {len(components)} components")
    
    # Generate simple CSV
    csv_path = Path("reports/dedupe/components_provenance.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'display_name', 'path', 'props_signature', 'file_size', 'lines_of_code', 'matches_contract', 'tokens_compliant', 'a11y_notes_present', 'usage_count', 'last_commit_date', 'first_commit_date', 'story_exists', 'props_signature_hash']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for component in components:
            writer.writerow(component)
    
    print(f"Generated CSV: {csv_path}")
    
    # Generate simple markdown
    md_path = Path("reports/dedupe/components_by_usage.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# Component Analysis\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total Components**: {len(components)}\n\n")
        
        f.write("## All Components\n\n")
        f.write("| Component | Path | Props | Size | Lines |\n")
        f.write("|-----------|------|-------|------|-------|\n")
        
        for component in components:
            f.write(f"| {component['display_name']} | {component['path']} | "
                   f"{'Yes' if component['props_signature'] != 'no_props' else 'No'} | "
                   f"{component['file_size']} | {component['lines_of_code']} |\n")
    
    print(f"Generated Markdown: {md_path}")

if __name__ == "__main__":
    scan_components()
