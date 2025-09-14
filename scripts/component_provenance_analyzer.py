#!/usr/bin/env python3
"""
Component Provenance Matrix Generator

Scans frontend codebase for React components and generates comprehensive
provenance analysis including usage patterns, compliance checks, and duplicate detection.
"""

import os
import re
import csv
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import json
import ast
import sys

@dataclass
class ComponentInfo:
    name: str
    path: str
    props_signature_hash: str
    first_commit_date: str
    last_commit_date: str
    usage_count: int
    story_exists: bool
    matches_contract: bool
    tokens_compliant: bool
    a11y_notes_present: bool
    display_name: str
    props_signature: str
    file_size: int
    lines_of_code: int
    imports: List[str]
    exports: List[str]

class ComponentProvenanceAnalyzer:
    def __init__(self, frontend_path: str = "frontend"):
        self.frontend_path = Path(frontend_path)
        self.src_path = self.frontend_path / "src"
        
        # Ensure we're in the right directory
        if not self.src_path.exists():
            # Try relative to current directory
            self.src_path = Path("frontend/src")
            if not self.src_path.exists():
                print(f"Warning: Frontend src path not found: {self.src_path}")
                return
        self.components: List[ComponentInfo] = []
        self.usage_map: Dict[str, int] = defaultdict(int)
        self.import_map: Dict[str, Set[str]] = defaultdict(set)
        self.component_contracts = self._load_component_contracts()
        
    def _load_component_contracts(self) -> Set[str]:
        """Load canonical component names from docs/frontend/components.md"""
        contracts_path = Path("docs/frontend/components.md")
        if not contracts_path.exists():
            return set()
            
        contracts = set()
        with open(contracts_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract component names from markdown
            # Look for patterns like **`ComponentName`**
            matches = re.findall(r'\*\*`([A-Z][a-zA-Z0-9]+)`\*\*', content)
            contracts.update(matches)
            
        return contracts
    
    def _normalize_component_name(self, name: str) -> str:
        """Normalize component names for comparison"""
        # Remove common suffixes and prefixes
        name = re.sub(r'\.(tsx?|jsx?)$', '', name)
        name = re.sub(r'^[A-Z]', lambda m: m.group(0).lower(), name)
        return name
    
    def _extract_props_signature(self, file_path: Path) -> Tuple[str, str]:
        """Extract props signature from TypeScript/JavaScript file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for interface definitions
            interface_pattern = r'interface\s+(\w+Props)\s*\{([^}]+)\}'
            interface_matches = re.findall(interface_pattern, content, re.DOTALL)
            
            if interface_matches:
                interface_name, props_content = interface_matches[0]
                # Clean up props content
                props_content = re.sub(r'\s+', ' ', props_content.strip())
                return interface_name, props_content
            
            # Look for type definitions
            type_pattern = r'type\s+(\w+Props)\s*=\s*\{([^}]+)\}'
            type_matches = re.findall(type_pattern, content, re.DOTALL)
            
            if type_matches:
                type_name, props_content = type_matches[0]
                props_content = re.sub(r'\s+', ' ', props_content.strip())
                return type_name, props_content
                
            # Look for inline props in function parameters
            func_pattern = r'function\s+\w+\s*\(\s*\{\s*([^}]+)\s*\}\s*:\s*(\w+Props)'
            func_matches = re.findall(func_pattern, content, re.DOTALL)
            
            if func_matches:
                props_content, type_name = func_matches[0]
                props_content = re.sub(r'\s+', ' ', props_content.strip())
                return type_name, props_content
                
            return "unknown", "no_props"
            
        except Exception as e:
            print(f"Error extracting props from {file_path}: {e}")
            return "error", "extraction_failed"
    
    def _get_git_dates(self, file_path: Path) -> Tuple[str, str]:
        """Get first and last commit dates for a file"""
        try:
            # Get first commit date
            first_cmd = ["git", "log", "--follow", "--format=%ai", "--reverse", str(file_path)]
            first_result = subprocess.run(first_cmd, capture_output=True, text=True, cwd=self.frontend_path.parent)
            first_date = first_result.stdout.strip().split('\n')[0] if first_result.stdout.strip() else "unknown"
            
            # Get last commit date
            last_cmd = ["git", "log", "--format=%ai", "-1", str(file_path)]
            last_result = subprocess.run(last_cmd, capture_output=True, text=True, cwd=self.frontend_path.parent)
            last_date = last_result.stdout.strip() if last_result.stdout.strip() else "unknown"
            
            return first_date, last_date
            
        except Exception as e:
            print(f"Error getting git dates for {file_path}: {e}")
            return "unknown", "unknown"
    
    def _check_story_exists(self, component_path: Path) -> bool:
        """Check if Storybook story exists for component"""
        component_name = component_path.stem
        story_patterns = [
            f"{component_name}.stories.tsx",
            f"{component_name}.stories.ts",
            f"{component_name}.stories.jsx",
            f"{component_name}.stories.js"
        ]
        
        # Check in same directory
        for pattern in story_patterns:
            if (component_path.parent / pattern).exists():
                return True
                
        # Check in stories directory
        stories_dir = component_path.parent / "stories"
        if stories_dir.exists():
            for pattern in story_patterns:
                if (stories_dir / pattern).exists():
                    return True
                    
        return False
    
    def _check_tokens_compliance(self, file_path: Path) -> bool:
        """Check if component uses design tokens"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for design token imports
            token_imports = [
                "design-tokens",
                "tokens",
                "theme",
                "designTokens"
            ]
            
            for token_import in token_imports:
                if token_import in content:
                    return True
                    
            # Look for CSS custom properties
            if "--" in content and "var(" in content:
                return True
                
            return False
            
        except Exception as e:
            print(f"Error checking tokens compliance for {file_path}: {e}")
            return False
    
    def _check_a11y_notes(self, file_path: Path) -> bool:
        """Check if component has accessibility notes"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for accessibility-related comments and code
            a11y_indicators = [
                "aria-",
                "role=",
                "tabIndex",
                "accessibility",
                "screen reader",
                "keyboard navigation",
                "focus management",
                "ARIA",
                "a11y"
            ]
            
            for indicator in a11y_indicators:
                if indicator in content:
                    return True
                    
            return False
            
        except Exception as e:
            print(f"Error checking a11y notes for {file_path}: {e}")
            return False
    
    def _extract_component_info(self, file_path: Path) -> Optional[ComponentInfo]:
        """Extract comprehensive component information"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                file_size = len(content.encode('utf-8'))
                lines_of_code = len(content.splitlines())
            
            # Extract component name from file
            component_name = file_path.stem
            
            # Extract display name (look for export default or named exports)
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
            
            # Extract props signature
            props_interface, props_signature = self._extract_props_signature(file_path)
            props_hash = hashlib.md5(props_signature.encode()).hexdigest()[:8]
            
            # Get git dates
            first_date, last_date = self._get_git_dates(file_path)
            
            # Check various compliance flags
            story_exists = self._check_story_exists(file_path)
            matches_contract = display_name in self.component_contracts
            tokens_compliant = self._check_tokens_compliance(file_path)
            a11y_notes_present = self._check_a11y_notes(file_path)
            
            # Extract imports and exports
            imports = re.findall(r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]', content)
            exports = re.findall(r'export\s+(?:default\s+)?(?:const|function|class)\s+(\w+)', content)
            
            return ComponentInfo(
                name=component_name,
                path=str(file_path.relative_to(self.frontend_path)),
                props_signature_hash=props_hash,
                first_commit_date=first_date,
                last_commit_date=last_date,
                usage_count=0,  # Will be calculated later
                story_exists=story_exists,
                matches_contract=matches_contract,
                tokens_compliant=tokens_compliant,
                a11y_notes_present=a11y_notes_present,
                display_name=display_name,
                props_signature=props_signature,
                file_size=file_size,
                lines_of_code=lines_of_code,
                imports=imports,
                exports=exports
            )
            
        except Exception as e:
            print(f"Error extracting component info from {file_path}: {e}")
            return None
    
    def _scan_components(self):
        """Scan for React components in the frontend directory"""
        print("Scanning for React components...")
        
        # Find all .tsx and .jsx files
        component_files = []
        for pattern in ["**/*.tsx", "**/*.jsx"]:
            component_files.extend(self.src_path.glob(pattern))
        
        print(f"Found {len(component_files)} component files")
        
        for file_path in component_files:
            # Skip test files and stories
            if any(skip in str(file_path) for skip in ['.test.', '.spec.', '.stories.']):
                continue
                
            component_info = self._extract_component_info(file_path)
            if component_info:
                self.components.append(component_info)
                print(f"  - {component_info.display_name} ({component_info.path})")
    
    def _analyze_usage(self):
        """Analyze component usage across the codebase"""
        print("Analyzing component usage...")
        
        # Scan all files for imports
        for file_path in self.src_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in ['.tsx', '.jsx', '.ts', '.js']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Look for imports of our components
                    for component in self.components:
                        # Check for various import patterns
                        import_patterns = [
                            f"import.*{component.display_name}.*from",
                            f"from.*{component.display_name}",
                            f"<{component.display_name}",
                            f"import.*{component.name}.*from",
                            f"from.*{component.name}",
                            f"<{component.name}"
                        ]
                        
                        for pattern in import_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                self.usage_map[component.display_name] += 1
                                self.import_map[component.display_name].add(str(file_path.relative_to(self.frontend_path)))
                                break
                                
                except Exception as e:
                    print(f"Error analyzing usage in {file_path}: {e}")
        
        # Update usage counts
        for component in self.components:
            component.usage_count = self.usage_map.get(component.display_name, 0)
    
    def _group_by_display_name(self) -> Dict[str, List[ComponentInfo]]:
        """Group components by normalized display name"""
        groups = defaultdict(list)
        
        for component in self.components:
            normalized_name = self._normalize_component_name(component.display_name)
            groups[normalized_name].append(component)
            
        return groups
    
    def _generate_csv_report(self):
        """Generate CSV report with component provenance data"""
        csv_path = Path("reports/dedupe/components_provenance.csv")
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"Generating CSV report: {csv_path}")
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'name', 'path', 'props_signature_hash', 'first_commit_date', 
                'last_commit_date', 'usage_count', 'story_exists', 'matches_contract',
                'tokens_compliant', 'a11y_notes_present', 'display_name', 
                'props_signature', 'file_size', 'lines_of_code'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for component in self.components:
                row = asdict(component)
                # Convert lists to strings for CSV
                row['imports'] = ';'.join(row['imports'])
                row['exports'] = ';'.join(row['exports'])
                # Remove the list fields from the row
                del row['imports']
                del row['exports']
                writer.writerow(row)
    
    def _generate_usage_report(self):
        """Generate markdown report with usage analysis"""
        md_path = Path("reports/dedupe/components_by_usage.md")
        md_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"Generating usage report: {md_path}")
        
        # Sort components by usage count
        sorted_components = sorted(self.components, key=lambda x: x.usage_count, reverse=True)
        
        # Group by display name to find duplicates
        groups = self._group_by_display_name()
        duplicates = {name: components for name, components in groups.items() if len(components) > 1}
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# Component Usage Analysis\n\n")
            from datetime import datetime
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Total Components**: {len(self.components)}\n")
            f.write(f"**Duplicate Groups**: {len(duplicates)}\n\n")
            
            # Top 50 by usage
            f.write("## Top 50 Components by Usage\n\n")
            f.write("| Rank | Component | Usage Count | Path | Contract Match | Tokens | A11y | Story |\n")
            f.write("|------|-----------|-------------|------|----------------|--------|------|-------|\n")
            
            for i, component in enumerate(sorted_components[:50], 1):
                f.write(f"| {i} | {component.display_name} | {component.usage_count} | {component.path} | "
                       f"{'✅' if component.matches_contract else '❌'} | "
                       f"{'✅' if component.tokens_compliant else '❌'} | "
                       f"{'✅' if component.a11y_notes_present else '❌'} | "
                       f"{'✅' if component.story_exists else '❌'} |\n")
            
            # Duplicate components
            f.write("\n## Duplicate Components (Multiple Files)\n\n")
            if duplicates:
                for name, components in duplicates.items():
                    f.write(f"### {name}\n\n")
                    f.write("| Path | Usage | Props Hash | Contract | Tokens | A11y | Story |\n")
                    f.write("|------|-------|------------|----------|--------|------|-------|\n")
                    
                    for component in components:
                        f.write(f"| {component.path} | {component.usage_count} | {component.props_signature_hash} | "
                               f"{'✅' if component.matches_contract else '❌'} | "
                               f"{'✅' if component.tokens_compliant else '❌'} | "
                               f"{'✅' if component.a11y_notes_present else '❌'} | "
                               f"{'✅' if component.story_exists else '❌'} |\n")
                    f.write("\n")
            else:
                f.write("No duplicate components found.\n")
            
            # Components in multiple folders
            f.write("\n## Components in Multiple Folders\n\n")
            folder_groups = defaultdict(list)
            for component in self.components:
                folder = str(Path(component.path).parent)
                folder_groups[folder].append(component)
            
            multi_folder_components = []
            for folder, components in folder_groups.items():
                for component in components:
                    # Check if this component name appears in other folders
                    other_folders = [f for f in folder_groups.keys() if f != folder]
                    for other_folder in other_folders:
                        other_components = folder_groups[other_folder]
                        if any(c.display_name == component.display_name for c in other_components):
                            multi_folder_components.append((component, folder, other_folder))
            
            if multi_folder_components:
                f.write("| Component | Primary Folder | Other Folders |\n")
                f.write("|-----------|----------------|---------------|\n")
                for component, primary, other in multi_folder_components:
                    f.write(f"| {component.display_name} | {primary} | {other} |\n")
            else:
                f.write("No components found in multiple folders.\n")
            
            # Summary statistics
            f.write("\n## Summary Statistics\n\n")
            f.write(f"- **Total Components**: {len(self.components)}\n")
            f.write(f"- **Components with Stories**: {sum(1 for c in self.components if c.story_exists)}\n")
            f.write(f"- **Components Matching Contract**: {sum(1 for c in self.components if c.matches_contract)}\n")
            f.write(f"- **Components Using Design Tokens**: {sum(1 for c in self.components if c.tokens_compliant)}\n")
            f.write(f"- **Components with A11y Notes**: {sum(1 for c in self.components if c.a11y_notes_present)}\n")
            f.write(f"- **Duplicate Component Groups**: {len(duplicates)}\n")
            f.write(f"- **Average Usage Count**: {sum(c.usage_count for c in self.components) / len(self.components):.1f}\n")
    
    def run_analysis(self):
        """Run the complete component provenance analysis"""
        print("Starting Component Provenance Analysis...")
        
        self._scan_components()
        self._analyze_usage()
        self._generate_csv_report()
        self._generate_usage_report()
        
        print(f"\nAnalysis complete!")
        print(f"- Found {len(self.components)} components")
        print(f"- Generated CSV report: reports/dedupe/components_provenance.csv")
        print(f"- Generated usage report: reports/dedupe/components_by_usage.md")

if __name__ == "__main__":
    analyzer = ComponentProvenanceAnalyzer()
    analyzer.run_analysis()