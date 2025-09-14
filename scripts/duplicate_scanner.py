#!/usr/bin/env python3
"""
Duplicate/Dead Code Scanner - SarvanOM v2

This script scans the codebase for duplications, unused code, and circular imports.

Backend Analysis:
- Duplicate FastAPI routers/endpoints (same path+method mounted more than once)
- Duplicate service modules by name
- Unused modules
- Circular imports that cause "double mount"

Frontend Analysis:
- Duplicate components with same public props but different locations
- Unused components
- Pages rendering both old and new versions of the same feature

Output:
- reports/duplications/backend.csv
- reports/duplications/frontend.csv
- docs/review/dup_candidates.csv (updated)
- docs/review/deprecation_notes.md (proposed moves)
"""

import os
import re
import json
import ast
import csv
import logging
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict, Counter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BackendDuplicate:
    file: str
    symbol: str
    duplicate_of: str
    referenced_by: str
    type: str  # 'endpoint', 'module', 'import', 'circular'
    severity: str  # 'high', 'medium', 'low'

@dataclass
class FrontendDuplicate:
    file: str
    symbol: str
    duplicate_of: str
    referenced_by: str
    type: str  # 'component', 'page', 'feature'
    severity: str  # 'high', 'medium', 'low'

class BackendDuplicateScanner:
    """Scans backend for duplicates and dead code"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.services_dir = self.project_root / "services"
        self.shared_dir = self.project_root / "shared"
        self.duplicates = []
        self.endpoints = defaultdict(list)
        self.modules = defaultdict(list)
        self.imports = defaultdict(list)
        
    def scan_all(self) -> List[BackendDuplicate]:
        """Scan all backend code for duplicates"""
        logger.info("Scanning backend for duplicates...")
        
        # Scan services directory
        self._scan_directory(self.services_dir)
        
        # Scan shared directory
        self._scan_directory(self.shared_dir)
        
        # Analyze findings
        self._analyze_endpoint_duplicates()
        self._analyze_module_duplicates()
        self._analyze_import_duplicates()
        self._analyze_circular_imports()
        
        return self.duplicates
    
    def _scan_directory(self, directory: Path):
        """Scan a directory for Python files"""
        if not directory.exists():
            return
            
        for py_file in directory.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
                
            try:
                self._scan_file(py_file)
            except Exception as e:
                logger.warning(f"Error scanning {py_file}: {e}")
    
    def _scan_file(self, file_path: Path):
        """Scan a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Find endpoints
            self._find_endpoints(file_path, content)
            
            # Find modules and imports
            self._find_modules_and_imports(file_path, tree)
            
        except Exception as e:
            logger.warning(f"Error parsing {file_path}: {e}")
    
    def _find_endpoints(self, file_path: Path, content: str):
        """Find FastAPI endpoints in file"""
        # Pattern to match FastAPI route decorators
        route_pattern = r'@app\.(get|post|put|delete|patch|head|options)\s*\(\s*["\']([^"\']+)["\']'
        
        matches = re.findall(route_pattern, content)
        for method, path in matches:
            endpoint_key = f"{method.upper()} {path}"
            self.endpoints[endpoint_key].append({
                'file': str(file_path.relative_to(self.project_root)),
                'method': method.upper(),
                'path': path
            })
    
    def _find_modules_and_imports(self, file_path: Path, tree: ast.AST):
        """Find module definitions and imports"""
        file_str = str(file_path.relative_to(self.project_root))
        
        # Find class and function definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self.modules[node.name].append({
                    'file': file_str,
                    'type': 'class',
                    'line': node.lineno
                })
            elif isinstance(node, ast.FunctionDef):
                self.modules[node.name].append({
                    'file': file_str,
                    'type': 'function',
                    'line': node.lineno
                })
        
        # Find imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports[alias.name].append({
                        'file': file_str,
                        'type': 'import',
                        'line': node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.imports[node.module].append({
                        'file': file_str,
                        'type': 'from_import',
                        'line': node.lineno
                    })
    
    def _analyze_endpoint_duplicates(self):
        """Analyze duplicate endpoints"""
        for endpoint_key, occurrences in self.endpoints.items():
            if len(occurrences) > 1:
                # Group by file to avoid false positives within same service
                files = defaultdict(list)
                for occurrence in occurrences:
                    files[occurrence['file']].append(occurrence)
                
                # Only flag if endpoints are in different files
                if len(files) > 1:
                    # Find the primary occurrence (usually the first one)
                    primary_file = min(files.keys())
                    primary = files[primary_file][0]
                    
                    for file_path, file_occurrences in files.items():
                        if file_path != primary_file:
                            for occurrence in file_occurrences:
                                duplicate = BackendDuplicate(
                                    file=occurrence['file'],
                                    symbol=f"{occurrence['method']} {occurrence['path']}",
                                    duplicate_of=primary['file'],
                                    referenced_by="FastAPI router",
                                    type="endpoint",
                                    severity="high"
                                )
                                self.duplicates.append(duplicate)
    
    def _analyze_module_duplicates(self):
        """Analyze duplicate module names"""
        for module_name, occurrences in self.modules.items():
            if len(occurrences) > 1:
                # Group by file to find duplicates within same file
                files = defaultdict(list)
                for occurrence in occurrences:
                    files[occurrence['file']].append(occurrence)
                
                # Check for duplicates across files
                if len(files) > 1:
                    primary_file = min(files.keys())
                    for file_path, file_occurrences in files.items():
                        if file_path != primary_file:
                            for occurrence in file_occurrences:
                                duplicate = BackendDuplicate(
                                    file=file_path,
                                    symbol=f"{occurrence['type']} {module_name}",
                                    duplicate_of=primary_file,
                                    referenced_by="module definition",
                                    type="module",
                                    severity="medium"
                                )
                                self.duplicates.append(duplicate)
    
    def _analyze_import_duplicates(self):
        """Analyze duplicate imports"""
        for import_name, occurrences in self.imports.items():
            if len(occurrences) > 1:
                # Group by file
                files = defaultdict(list)
                for occurrence in occurrences:
                    files[occurrence['file']].append(occurrence)
                
                # Check for duplicate imports within same file
                for file_path, file_occurrences in files.items():
                    if len(file_occurrences) > 1:
                        # Find the first occurrence as primary
                        primary = file_occurrences[0]
                        for occurrence in file_occurrences[1:]:
                            duplicate = BackendDuplicate(
                                file=file_path,
                                symbol=f"import {import_name}",
                                duplicate_of=f"{file_path}:{primary['line']}",
                                referenced_by="import statement",
                                type="import",
                                severity="low"
                            )
                            self.duplicates.append(duplicate)
    
    def _analyze_circular_imports(self):
        """Analyze potential circular imports"""
        # Skip standard library imports that are commonly used
        standard_libs = {
            'asyncio', 'json', 'logging', 'time', 'datetime', 'pathlib', 'typing',
            'dataclasses', 'enum', 'collections', 're', 'os', 'sys', 'uuid',
            'hashlib', 'base64', 'urllib', 'http', 'socket', 'ssl', 'threading',
            'multiprocessing', 'concurrent', 'functools', 'itertools', 'operator'
        }
        
        for import_name, occurrences in self.imports.items():
            # Skip standard library imports
            if import_name in standard_libs:
                continue
                
            if len(occurrences) > 1:
                # Check if imports are in different files that might import each other
                files = set(occurrence['file'] for occurrence in occurrences)
                if len(files) > 1:
                    # Only flag if it's a project-specific import
                    if not import_name.startswith(('http', 'fastapi', 'pydantic', 'redis', 'sqlalchemy')):
                        for file_path in files:
                            duplicate = BackendDuplicate(
                                file=file_path,
                                symbol=f"circular import {import_name}",
                                duplicate_of="circular dependency",
                                referenced_by="import chain",
                                type="circular",
                                severity="high"
                            )
                            self.duplicates.append(duplicate)

class FrontendDuplicateScanner:
    """Scans frontend for duplicates and dead code"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.frontend_dir = self.project_root / "frontend" / "src"
        self.duplicates = []
        self.components = defaultdict(list)
        self.pages = defaultdict(list)
        
    def scan_all(self) -> List[FrontendDuplicate]:
        """Scan all frontend code for duplicates"""
        logger.info("Scanning frontend for duplicates...")
        
        # Scan components
        self._scan_components()
        
        # Scan pages
        self._scan_pages()
        
        # Analyze findings
        self._analyze_component_duplicates()
        self._analyze_page_duplicates()
        self._analyze_unused_components()
        
        return self.duplicates
    
    def _scan_components(self):
        """Scan component files"""
        components_dir = self.frontend_dir / "components"
        if not components_dir.exists():
            return
            
        for tsx_file in components_dir.rglob("*.tsx"):
            try:
                self._scan_component_file(tsx_file)
            except Exception as e:
                logger.warning(f"Error scanning component {tsx_file}: {e}")
    
    def _scan_component_file(self, file_path: Path):
        """Scan a single component file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract component name from filename
            component_name = file_path.stem
            
            # Find component definition
            component_pattern = r'(?:export\s+)?(?:default\s+)?(?:function|const)\s+(\w+)\s*[=\(]'
            matches = re.findall(component_pattern, content)
            
            for match in matches:
                if match == component_name or match.startswith(component_name):
                    # Extract props interface if present
                    props_interface = self._extract_props_interface(content)
                    
                    self.components[component_name].append({
                        'file': str(file_path.relative_to(self.project_root)),
                        'props': props_interface,
                        'content': content[:500]  # First 500 chars for comparison
                    })
                    
        except Exception as e:
            logger.warning(f"Error parsing component {file_path}: {e}")
    
    def _extract_props_interface(self, content: str) -> str:
        """Extract props interface from component"""
        # Look for interface definitions
        interface_pattern = r'interface\s+(\w*Props)\s*\{([^}]+)\}'
        matches = re.findall(interface_pattern, content, re.DOTALL)
        
        if matches:
            return matches[0][1].strip()
        
        # Look for type definitions
        type_pattern = r'type\s+(\w*Props)\s*=\s*\{([^}]+)\}'
        matches = re.findall(type_pattern, content, re.DOTALL)
        
        if matches:
            return matches[0][1].strip()
        
        return ""
    
    def _scan_pages(self):
        """Scan page files"""
        app_dir = self.frontend_dir / "app"
        if not app_dir.exists():
            return
            
        for page_file in app_dir.rglob("page.tsx"):
            try:
                self._scan_page_file(page_file)
            except Exception as e:
                logger.warning(f"Error scanning page {page_file}: {e}")
    
    def _scan_page_file(self, file_path: Path):
        """Scan a single page file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract page path
            page_path = self._get_page_path(file_path)
            
            # Find imported components
            import_pattern = r'import\s+.*?\s+from\s+["\']([^"\']+)["\']'
            imports = re.findall(import_pattern, content)
            
            # Find component usage
            component_pattern = r'<(\w+)(?:\s|>)'
            components = re.findall(component_pattern, content)
            
            self.pages[page_path].append({
                'file': str(file_path.relative_to(self.project_root)),
                'imports': imports,
                'components': components,
                'content': content[:500]
            })
            
        except Exception as e:
            logger.warning(f"Error parsing page {file_path}: {e}")
    
    def _get_page_path(self, file_path: Path) -> str:
        """Convert page file path to route path"""
        # Remove the frontend/src/app prefix
        relative_path = file_path.relative_to(self.frontend_dir / "app")
        
        # Remove page.tsx
        if relative_path.name == "page.tsx":
            route_path = str(relative_path.parent)
        else:
            route_path = str(relative_path)
        
        # Handle special cases
        if route_path == ".":
            return "/"
        
        # Convert to URL path
        route_path = "/" + route_path.replace("\\", "/")
        route_path = route_path.replace("//", "/")
        
        # Handle route groups (parentheses)
        route_path = re.sub(r'\([^)]+\)', '', route_path)
        route_path = route_path.replace("//", "/")
        
        return route_path
    
    def _analyze_component_duplicates(self):
        """Analyze duplicate components"""
        for component_name, occurrences in self.components.items():
            if len(occurrences) > 1:
                # Group by props interface
                props_groups = defaultdict(list)
                for occurrence in occurrences:
                    props_key = occurrence['props'] or 'no_props'
                    props_groups[props_key].append(occurrence)
                
                # Check for duplicates with same props
                for props_key, props_occurrences in props_groups.items():
                    if len(props_occurrences) > 1:
                        primary = props_occurrences[0]
                        for occurrence in props_occurrences[1:]:
                            duplicate = FrontendDuplicate(
                                file=occurrence['file'],
                                symbol=f"component {component_name}",
                                duplicate_of=primary['file'],
                                referenced_by="component definition",
                                type="component",
                                severity="high"
                            )
                            self.duplicates.append(duplicate)
    
    def _analyze_page_duplicates(self):
        """Analyze duplicate page functionality"""
        for page_path, occurrences in self.pages.items():
            if len(occurrences) > 1:
                # Check for similar functionality
                primary = occurrences[0]
                for occurrence in occurrences[1:]:
                    # Compare component usage
                    common_components = set(primary['components']) & set(occurrence['components'])
                    if len(common_components) > 2:  # Threshold for similarity
                        duplicate = FrontendDuplicate(
                            file=occurrence['file'],
                            symbol=f"page {page_path}",
                            duplicate_of=primary['file'],
                            referenced_by="page rendering",
                            type="page",
                            severity="medium"
                        )
                        self.duplicates.append(duplicate)
    
    def _analyze_unused_components(self):
        """Analyze unused components"""
        # Get all component names
        all_components = set(self.components.keys())
        
        # Get all used components from pages
        used_components = set()
        for page_occurrences in self.pages.values():
            for occurrence in page_occurrences:
                used_components.update(occurrence['components'])
        
        # Find unused components
        unused_components = all_components - used_components
        
        for component_name in unused_components:
            for occurrence in self.components[component_name]:
                duplicate = FrontendDuplicate(
                    file=occurrence['file'],
                    symbol=f"unused component {component_name}",
                    duplicate_of="unused",
                    referenced_by="none",
                    type="component",
                    severity="low"
                )
                self.duplicates.append(duplicate)

def generate_backend_csv(duplicates: List[BackendDuplicate], output_path: Path):
    """Generate backend duplicates CSV"""
    logger.info(f"Generating backend CSV: {output_path}")
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['file', 'symbol', 'duplicate_of', 'referenced_by', 'type', 'severity'])
        
        for duplicate in duplicates:
            writer.writerow([
                duplicate.file,
                duplicate.symbol,
                duplicate.duplicate_of,
                duplicate.referenced_by,
                duplicate.type,
                duplicate.severity
            ])

def generate_frontend_csv(duplicates: List[FrontendDuplicate], output_path: Path):
    """Generate frontend duplicates CSV"""
    logger.info(f"Generating frontend CSV: {output_path}")
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['file', 'symbol', 'duplicate_of', 'referenced_by', 'type', 'severity'])
        
        for duplicate in duplicates:
            writer.writerow([
                duplicate.file,
                duplicate.symbol,
                duplicate.duplicate_of,
                duplicate.referenced_by,
                duplicate.type,
                duplicate.severity
            ])

def update_dup_candidates(backend_duplicates: List[BackendDuplicate], 
                         frontend_duplicates: List[FrontendDuplicate], 
                         output_path: Path):
    """Update or create dup_candidates.csv"""
    logger.info(f"Updating dup candidates: {output_path}")
    
    # Combine all duplicates
    all_duplicates = []
    
    for duplicate in backend_duplicates:
        all_duplicates.append({
            'file': duplicate.file,
            'symbol': duplicate.symbol,
            'duplicate_of': duplicate.duplicate_of,
            'referenced_by': duplicate.referenced_by,
            'type': duplicate.type,
            'severity': duplicate.severity,
            'category': 'backend'
        })
    
    for duplicate in frontend_duplicates:
        all_duplicates.append({
            'file': duplicate.file,
            'symbol': duplicate.symbol,
            'duplicate_of': duplicate.duplicate_of,
            'referenced_by': duplicate.referenced_by,
            'type': duplicate.type,
            'severity': duplicate.severity,
            'category': 'frontend'
        })
    
    # Sort by severity and type
    severity_order = {'high': 0, 'medium': 1, 'low': 2}
    all_duplicates.sort(key=lambda x: (severity_order.get(x['severity'], 3), x['type']))
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['file', 'symbol', 'duplicate_of', 'referenced_by', 'type', 'severity', 'category'])
        
        for duplicate in all_duplicates:
            writer.writerow([
                duplicate['file'],
                duplicate['symbol'],
                duplicate['duplicate_of'],
                duplicate['referenced_by'],
                duplicate['type'],
                duplicate['severity'],
                duplicate['category']
            ])

def generate_deprecation_notes(backend_duplicates: List[BackendDuplicate], 
                              frontend_duplicates: List[FrontendDuplicate], 
                              output_path: Path):
    """Generate deprecation notes with proposed moves"""
    logger.info(f"Generating deprecation notes: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Deprecation Notes - SarvanOM v2\n\n")
        f.write(f"**Generated**: {datetime.now().isoformat()}\n")
        f.write("**Purpose**: Proposed safe moves to /deprecated/ directory\n\n")
        
        # Backend deprecations
        f.write("## Backend Deprecations\n\n")
        
        backend_by_severity = defaultdict(list)
        for duplicate in backend_duplicates:
            backend_by_severity[duplicate.severity].append(duplicate)
        
        for severity in ['high', 'medium', 'low']:
            if severity in backend_by_severity:
                f.write(f"### {severity.title()} Priority\n\n")
                for duplicate in backend_by_severity[severity]:
                    f.write(f"**File**: `{duplicate.file}`\n")
                    f.write(f"**Symbol**: {duplicate.symbol}\n")
                    f.write(f"**Duplicate Of**: `{duplicate.duplicate_of}`\n")
                    f.write(f"**Proposed Move**: `deprecated/backend/{duplicate.file}`\n")
                    f.write(f"**Reason**: {duplicate.type} duplication\n\n")
        
        # Frontend deprecations
        f.write("## Frontend Deprecations\n\n")
        
        frontend_by_severity = defaultdict(list)
        for duplicate in frontend_duplicates:
            frontend_by_severity[duplicate.severity].append(duplicate)
        
        for severity in ['high', 'medium', 'low']:
            if severity in frontend_by_severity:
                f.write(f"### {severity.title()} Priority\n\n")
                for duplicate in frontend_by_severity[severity]:
                    f.write(f"**File**: `{duplicate.file}`\n")
                    f.write(f"**Symbol**: {duplicate.symbol}\n")
                    f.write(f"**Duplicate Of**: `{duplicate.duplicate_of}`\n")
                    f.write(f"**Proposed Move**: `deprecated/frontend/{duplicate.file}`\n")
                    f.write(f"**Reason**: {duplicate.type} duplication\n\n")
        
        # Summary
        f.write("## Summary\n\n")
        f.write(f"- **Backend Duplicates**: {len(backend_duplicates)}\n")
        f.write(f"- **Frontend Duplicates**: {len(frontend_duplicates)}\n")
        f.write(f"- **Total Duplicates**: {len(backend_duplicates) + len(frontend_duplicates)}\n\n")
        
        f.write("## Next Steps\n\n")
        f.write("1. Review proposed moves for safety\n")
        f.write("2. Create /deprecated/ directory structure\n")
        f.write("3. Move files to deprecated locations\n")
        f.write("4. Update import statements\n")
        f.write("5. Test application functionality\n")

def main():
    """Main function"""
    project_root = Path(__file__).parent.parent
    
    # Create output directories
    output_dir = project_root / "reports" / "duplications"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    docs_review_dir = project_root / "docs" / "review"
    docs_review_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Starting duplicate/dead-code scan...")
    
    # Scan backend
    backend_scanner = BackendDuplicateScanner(project_root)
    backend_duplicates = backend_scanner.scan_all()
    
    # Scan frontend
    frontend_scanner = FrontendDuplicateScanner(project_root)
    frontend_duplicates = frontend_scanner.scan_all()
    
    # Generate reports
    generate_backend_csv(backend_duplicates, output_dir / "backend.csv")
    generate_frontend_csv(frontend_duplicates, output_dir / "frontend.csv")
    update_dup_candidates(backend_duplicates, frontend_duplicates, docs_review_dir / "dup_candidates.csv")
    generate_deprecation_notes(backend_duplicates, frontend_duplicates, docs_review_dir / "deprecation_notes.md")
    
    logger.info("Duplicate/dead-code scan complete!")
    logger.info(f"Backend duplicates: {len(backend_duplicates)}")
    logger.info(f"Frontend duplicates: {len(frontend_duplicates)}")
    logger.info(f"Reports generated in: {output_dir}")

if __name__ == "__main__":
    main()
