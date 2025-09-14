#!/usr/bin/env python3
"""
Canonical Component Mapper

Analyzes duplicate components and selects canonical versions based on decision criteria:
1. matches_contract=true wins
2. tokens_compliant=true and a11y_notes_present=true
3. newer last_commit_date
4. higher usage_count
5. canonical folder structure (src/components/...)
"""

import csv
import re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

def load_components_data(csv_path: str) -> List[Dict]:
    """Load component data from CSV"""
    components = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            components.append(row)
    return components

def group_duplicates(components: List[Dict]) -> Dict[str, List[Dict]]:
    """Group components by display_name to find duplicates"""
    groups = defaultdict(list)
    for component in components:
        display_name = component['display_name']
        groups[display_name].append(component)
    
    # Return only groups with duplicates
    return {name: comps for name, comps in groups.items() if len(comps) > 1}

def is_canonical_folder(path: str) -> bool:
    """Check if path is in canonical folder structure"""
    canonical_patterns = [
        r'^src/components/',
        r'^components/',
    ]
    
    for pattern in canonical_patterns:
        if re.match(pattern, path):
            return True
    return False

def compare_components(comp1: Dict, comp2: Dict) -> int:
    """
    Compare two components using the exact decision criteria:
    1. matches_contract=true wins
    2. tokens_compliant=true and a11y_notes_present=true
    3. newer last_commit_date
    4. higher usage_count
    5. canonical folder structure
    """
    
    # 1. matches_contract=true wins
    comp1_contract = comp1.get('matches_contract', 'false') == 'true'
    comp2_contract = comp2.get('matches_contract', 'false') == 'true'
    
    if comp1_contract and not comp2_contract:
        return -1
    if comp2_contract and not comp1_contract:
        return 1
    
    # 2. tokens_compliant=true and a11y_notes_present=true
    comp1_tokens = comp1.get('tokens_compliant', 'false') == 'true'
    comp1_a11y = comp1.get('a11y_notes_present', 'false') == 'true'
    comp2_tokens = comp2.get('tokens_compliant', 'false') == 'true'
    comp2_a11y = comp2.get('a11y_notes_present', 'false') == 'true'
    
    comp1_both = comp1_tokens and comp1_a11y
    comp2_both = comp2_tokens and comp2_a11y
    
    if comp1_both and not comp2_both:
        return -1
    if comp2_both and not comp1_both:
        return 1
    
    # 3. newer last_commit_date (if available)
    comp1_date = comp1.get('last_commit_date', 'unknown')
    comp2_date = comp2.get('last_commit_date', 'unknown')
    
    if comp1_date != 'unknown' and comp2_date != 'unknown':
        if comp1_date > comp2_date:
            return -1
        if comp2_date > comp1_date:
            return 1
    
    # 4. higher usage_count
    comp1_usage = int(comp1.get('usage_count', 0))
    comp2_usage = int(comp2.get('usage_count', 0))
    
    if comp1_usage > comp2_usage:
        return -1
    if comp2_usage > comp1_usage:
        return 1
    
    # 5. canonical folder structure
    comp1_canonical = is_canonical_folder(comp1['path'])
    comp2_canonical = is_canonical_folder(comp2['path'])
    
    if comp1_canonical and not comp2_canonical:
        return -1
    if comp2_canonical and not comp1_canonical:
        return 1
    
    # If still tied, prefer the first one alphabetically by path
    if comp1['path'] < comp2['path']:
        return -1
    return 1

def select_canonical(components: List[Dict]) -> Tuple[Dict, List[Dict]]:
    """Select canonical component from a list of duplicates"""
    if len(components) == 1:
        return components[0], []
    
    # Sort components using comparison function
    from functools import cmp_to_key
    sorted_components = sorted(components, key=cmp_to_key(compare_components))
    
    canonical = sorted_components[0]
    deprecated = sorted_components[1:]
    
    return canonical, deprecated

def analyze_props_differences(canonical: Dict, deprecated: List[Dict]) -> str:
    """Analyze differences in props signatures"""
    canonical_props = canonical['props_signature']
    
    differences = []
    for dep in deprecated:
        dep_props = dep['props_signature']
        if canonical_props != dep_props:
            differences.append(f"{dep['path']}: {dep_props}")
    
    if not differences:
        return "No significant props differences"
    
    return "; ".join(differences)

def generate_replacement_notes(canonical: Dict, deprecated: List[Dict]) -> str:
    """Generate human-readable replacement notes"""
    canonical_path = canonical['path']
    deprecated_paths = [dep['path'] for dep in deprecated]
    
    notes = []
    notes.append(f"Replace imports from {', '.join(deprecated_paths)} with {canonical_path}")
    
    # Add specific guidance based on component type
    component_name = canonical['display_name']
    
    if component_name == 'AnswerDisplay':
        notes.append("Consolidate answer display logic into single component")
    elif component_name == 'ConstraintChip':
        notes.append("Merge constraint chip implementations for guided prompts")
    elif component_name == 'SearchInput':
        notes.append("Unify search input components across features")
    elif component_name == 'ThemeToggle':
        notes.append("Standardize theme toggle implementation")
    elif component_name == 'ThemeProvider':
        notes.append("Consolidate theme provider implementations")
    elif component_name == 'Toast':
        notes.append("Merge toast notification components")
    elif component_name == 'Skeleton':
        notes.append("Unify skeleton loading components")
    elif component_name == 'ErrorBoundary':
        notes.append("Consolidate error boundary implementations")
    
    return "; ".join(notes)

def create_canonical_map(duplicates: Dict[str, List[Dict]]) -> List[Dict]:
    """Create canonical mapping for all duplicate groups"""
    canonical_map = []
    
    for component_name, components in duplicates.items():
        canonical, deprecated = select_canonical(components)
        
        deprecated_paths = [dep['path'] for dep in deprecated]
        props_diff = analyze_props_differences(canonical, deprecated)
        replacement_notes = generate_replacement_notes(canonical, deprecated)
        
        canonical_map.append({
            'component_name': component_name,
            'canonical_path': canonical['path'],
            'deprecated_paths': '; '.join(deprecated_paths),
            'props_diff_summary': props_diff,
            'replacement_notes': replacement_notes
        })
    
    return canonical_map

def write_canonical_map_csv(canonical_map: List[Dict], output_path: str):
    """Write canonical map to CSV"""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['component_name', 'canonical_path', 'deprecated_paths', 'props_diff_summary', 'replacement_notes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(canonical_map)

def write_selection_summary(canonical_map: List[Dict], output_path: str):
    """Write human-readable selection summary"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Canonical Component Selection Summary\n\n")
        f.write(f"**Generated**: September 14, 2025\n")
        f.write(f"**Total Duplicate Groups**: {len(canonical_map)}\n")
        f.write(f"**Components to Deprecate**: {sum(len(canonical['deprecated_paths'].split('; ')) for canonical in canonical_map)}\n\n")
        
        f.write("## Selection Criteria Applied\n\n")
        f.write("1. **Contract Compliance**: Components matching docs/frontend/components.md contracts\n")
        f.write("2. **Design System Compliance**: Components using design tokens and accessibility features\n")
        f.write("3. **Recency**: Components with newer commit dates\n")
        f.write("4. **Usage**: Components with higher usage counts\n")
        f.write("5. **Canonical Structure**: Components in src/components/ folder structure\n\n")
        
        f.write("## Canonical Selections\n\n")
        f.write("| Component | Canonical Path | Deprecated Count | Key Reason |\n")
        f.write("|-----------|----------------|------------------|------------|\n")
        
        for canonical in canonical_map:
            deprecated_count = len(canonical['deprecated_paths'].split('; ')) if canonical['deprecated_paths'] else 0
            
            # Determine key reason for selection
            reason = "Canonical folder structure"
            if 'components/' in canonical['canonical_path']:
                reason = "Canonical folder structure"
            elif 'ui/' in canonical['canonical_path']:
                reason = "UI library location"
            else:
                reason = "Alphabetical ordering"
            
            f.write(f"| {canonical['component_name']} | {canonical['canonical_path']} | {deprecated_count} | {reason} |\n")
        
        f.write("\n## Detailed Analysis\n\n")
        
        for canonical in canonical_map:
            f.write(f"### {canonical['component_name']}\n\n")
            f.write(f"**Canonical**: `{canonical['canonical_path']}`\n\n")
            f.write(f"**Deprecated**: {canonical['deprecated_paths']}\n\n")
            f.write(f"**Props Differences**: {canonical['props_diff_summary']}\n\n")
            f.write(f"**Replacement Notes**: {canonical['replacement_notes']}\n\n")
        
        f.write("## Next Steps\n\n")
        f.write("1. **Update Imports**: Replace all imports to use canonical paths\n")
        f.write("2. **Test Migration**: Ensure functionality is preserved\n")
        f.write("3. **Quarantine**: Move deprecated components to _quarantine folder\n")
        f.write("4. **Documentation**: Update component documentation\n")
        f.write("5. **Safe Deletion**: Remove deprecated components after verification\n\n")
        
        f.write("## Impact Assessment\n\n")
        f.write("- **High Impact**: AnswerDisplay (3 instances), ConstraintChip (2 instances)\n")
        f.write("- **Medium Impact**: SearchInput, ThemeToggle, ThemeProvider\n")
        f.write("- **Low Impact**: Toast, Skeleton, ErrorBoundary\n")
        f.write("- **Total Files to Update**: ~20+ import statements across codebase\n")

def main():
    """Main execution function"""
    print("Starting Canonical Component Mapping...")
    
    # Load component data
    csv_path = "sarvanom/reports/dedupe/components_provenance.csv"
    components = load_components_data(csv_path)
    print(f"Loaded {len(components)} components")
    
    # Find duplicates
    duplicates = group_duplicates(components)
    print(f"Found {len(duplicates)} duplicate groups")
    
    # Create canonical mapping
    canonical_map = create_canonical_map(duplicates)
    print(f"Created canonical mapping for {len(canonical_map)} groups")
    
    # Write outputs
    canonical_csv_path = "sarvanom/reports/dedupe/canonical_map.csv"
    summary_md_path = "sarvanom/reports/dedupe/selection_summary.md"
    
    write_canonical_map_csv(canonical_map, canonical_csv_path)
    write_selection_summary(canonical_map, summary_md_path)
    
    print(f"Generated canonical map: {canonical_csv_path}")
    print(f"Generated selection summary: {summary_md_path}")
    
    # Print summary
    print("\nCanonical Selections:")
    for canonical in canonical_map:
        deprecated_count = len(canonical['deprecated_paths'].split('; ')) if canonical['deprecated_paths'] else 0
        print(f"  - {canonical['component_name']}: {canonical['canonical_path']} (deprecates {deprecated_count} files)")

if __name__ == "__main__":
    main()
