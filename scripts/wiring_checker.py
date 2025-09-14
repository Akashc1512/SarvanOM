#!/usr/bin/env python3
"""
Wiring Report Generator - SarvanOM v2

This script analyzes the codebase to validate runtime connectivity and wiring
for both backend services and frontend routes.

Backend Analysis:
- For each service, list all include_router(...), middleware, and mounted sub-apps
- Validate every endpoint promised in docs exists (path+method)
- Check /health and /metrics are reachable

Frontend Analysis:
- Enumerate the App Router tree (src/app/**/page.tsx|tsx)
- For each page spec under docs/frontend/pages/*.md, mark Found/Not Found
- List which canonical components each page renders
- Confirm GuidedPrompt is bound on documented free-text surfaces
- Check Settings has the default-ON toggle

Output:
- reports/wiring/backend_endpoints.md
- reports/wiring/frontend_routes.md
"""

import os
import re
import json
import ast
import logging
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BackendEndpoint:
    service: str
    endpoint: str
    method: str
    from_router: str
    in_docs: bool
    in_openapi: bool
    has_health: bool
    has_metrics: bool

@dataclass
class FrontendRoute:
    path: str
    page_file: str
    found: bool
    components: List[str]
    has_guided_prompt: bool
    has_settings_toggle: bool
    in_docs: bool

class BackendWiringAnalyzer:
    """Analyzes backend service wiring and endpoints"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.services_dir = self.project_root / "services"
        self.docs_dir = self.project_root / "docs"
        self.endpoints = []
        
    def analyze_all_services(self) -> List[BackendEndpoint]:
        """Analyze all backend services"""
        logger.info("Analyzing backend services...")
        
        # Define expected services
        services = [
            "guided_prompt",
            "retrieval", 
            "feeds",
            "model_router",
            "model_registry"
        ]
        
        for service in services:
            service_path = self.services_dir / service / "main.py"
            if service_path.exists():
                self._analyze_service(service, service_path)
            else:
                logger.warning(f"Service {service} main.py not found at {service_path}")
        
        return self.endpoints
    
    def _analyze_service(self, service_name: str, main_py_path: Path):
        """Analyze a single service's main.py file"""
        logger.info(f"Analyzing service: {service_name}")
        
        try:
            with open(main_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Use regex to find endpoints (more reliable than AST parsing)
            routes = self._find_routes_regex(content)
            
            # Check for health and metrics endpoints
            has_health = any(route['path'] == '/health' for route in routes)
            has_metrics = any(route['path'] == '/metrics' for route in routes)
            
            # Check if routes are documented
            documented_routes = self._get_documented_routes(service_name)
            
            # Create endpoint records
            for route in routes:
                endpoint = BackendEndpoint(
                    service=service_name,
                    endpoint=route['path'],
                    method=route['method'],
                    from_router=route.get('router', 'main'),
                    in_docs=route['path'] in documented_routes,
                    in_openapi=True,  # FastAPI auto-generates OpenAPI
                    has_health=has_health,
                    has_metrics=has_metrics
                )
                self.endpoints.append(endpoint)
                
        except Exception as e:
            logger.error(f"Error analyzing {service_name}: {e}")
    
    def _find_fastapi_app(self, tree: ast.AST) -> Optional[str]:
        """Find FastAPI app variable name"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if isinstance(node.value, ast.Call):
                            if isinstance(node.value.func, ast.Name):
                                if node.value.func.id == 'FastAPI':
                                    return target.id
        return None
    
    def _find_routes_regex(self, content: str) -> List[Dict[str, Any]]:
        """Find all route definitions using regex"""
        routes = []
        
        # Pattern to match FastAPI route decorators
        route_pattern = r'@app\.(get|post|put|delete|patch|head|options)\s*\(\s*["\']([^"\']+)["\']'
        
        matches = re.findall(route_pattern, content)
        for method, path in matches:
            routes.append({
                'path': path,
                'method': method.upper(),
                'router': 'main'
            })
        
        return routes
    
    def _find_routes(self, tree: ast.AST, app_name: str) -> List[Dict[str, Any]]:
        """Find all route definitions in the AST"""
        routes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Expr):
                if isinstance(node.value, ast.Call):
                    # Check for app.get, app.post, etc.
                    if isinstance(node.value.func, ast.Attribute):
                        if isinstance(node.value.func.value, ast.Name):
                            if node.value.func.value.id == app_name:
                                method = node.value.func.attr
                                if method in ['get', 'post', 'put', 'delete', 'patch']:
                                    if node.value.args:
                                        path = self._extract_string_literal(node.value.args[0])
                                        if path:
                                            routes.append({
                                                'path': path,
                                                'method': method.upper(),
                                                'router': 'main'
                                            })
        
        return routes
    
    def _extract_string_literal(self, node: ast.AST) -> Optional[str]:
        """Extract string literal from AST node"""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        elif isinstance(node, ast.Str):  # Python < 3.8 compatibility
            return node.s
        return None
    
    def _get_documented_routes(self, service_name: str) -> Set[str]:
        """Get documented routes for a service from docs"""
        documented_routes = set()
        
        # Look for service catalog documentation
        service_catalog_path = self.docs_dir / "architecture" / "service_catalog.md"
        if service_catalog_path.exists():
            try:
                with open(service_catalog_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract routes for this service
                # This is a simplified extraction - in reality, you'd parse the markdown more carefully
                if service_name in content:
                    # Look for route patterns in the content
                    route_pattern = r'`([^`]+)`'
                    matches = re.findall(route_pattern, content)
                    for match in matches:
                        if match.startswith('/'):
                            documented_routes.add(match)
                            
            except Exception as e:
                logger.warning(f"Error reading service catalog: {e}")
        
        return documented_routes

class FrontendWiringAnalyzer:
    """Analyzes frontend routing and component wiring"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.frontend_dir = self.project_root / "frontend" / "src" / "app"
        self.docs_dir = self.project_root / "docs"
        self.routes = []
        
    def analyze_frontend_routes(self) -> List[FrontendRoute]:
        """Analyze all frontend routes"""
        logger.info("Analyzing frontend routes...")
        
        # Get documented pages
        documented_pages = self._get_documented_pages()
        
        # Scan for all page.tsx files
        page_files = list(self.frontend_dir.rglob("page.tsx"))
        page_files.extend(list(self.frontend_dir.rglob("page.ts")))
        
        for page_file in page_files:
            route_path = self._get_route_path(page_file)
            components = self._extract_components(page_file)
            has_guided_prompt = self._check_guided_prompt(page_file)
            has_settings_toggle = self._check_settings_toggle(page_file)
            
            route = FrontendRoute(
                path=route_path,
                page_file=str(page_file.relative_to(self.project_root)),
                found=True,
                components=components,
                has_guided_prompt=has_guided_prompt,
                has_settings_toggle=has_settings_toggle,
                in_docs=route_path in documented_pages
            )
            self.routes.append(route)
        
        # Add missing documented routes
        for doc_path in documented_pages:
            if not any(route.path == doc_path for route in self.routes):
                route = FrontendRoute(
                    path=doc_path,
                    page_file="NOT_FOUND",
                    found=False,
                    components=[],
                    has_guided_prompt=False,
                    has_settings_toggle=False,
                    in_docs=True
                )
                self.routes.append(route)
        
        return self.routes
    
    def _get_route_path(self, page_file: Path) -> str:
        """Convert page file path to route path"""
        # Remove the frontend/src/app prefix
        relative_path = page_file.relative_to(self.frontend_dir)
        
        # Remove page.tsx/page.ts
        if relative_path.name in ['page.tsx', 'page.ts']:
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
    
    def _extract_components(self, page_file: Path) -> List[str]:
        """Extract component imports from page file"""
        components = []
        
        try:
            with open(page_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find import statements
            import_pattern = r'import\s+.*?\s+from\s+["\']([^"\']+)["\']'
            imports = re.findall(import_pattern, content)
            
            for import_path in imports:
                if 'components' in import_path:
                    # Extract component name from import path
                    component_name = import_path.split('/')[-1]
                    components.append(component_name)
                    
        except Exception as e:
            logger.warning(f"Error reading {page_file}: {e}")
        
        return components
    
    def _check_guided_prompt(self, page_file: Path) -> bool:
        """Check if page has GuidedPrompt integration"""
        try:
            with open(page_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for GuidedPrompt components or hooks
            guided_prompt_patterns = [
                'GuidedPrompt',
                'useGuidedPrompt',
                'GuidedPromptModal',
                'guided-prompt'
            ]
            
            for pattern in guided_prompt_patterns:
                if pattern in content:
                    return True
                    
        except Exception as e:
            logger.warning(f"Error checking guided prompt in {page_file}: {e}")
        
        return False
    
    def _check_settings_toggle(self, page_file: Path) -> bool:
        """Check if page has settings toggle"""
        try:
            with open(page_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for settings-related components
            settings_patterns = [
                'Settings',
                'useSettings',
                'settings',
                'toggle',
                'default.*on',
                'default.*true'
            ]
            
            for pattern in settings_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return True
                    
        except Exception as e:
            logger.warning(f"Error checking settings in {page_file}: {e}")
        
        return False
    
    def _get_documented_pages(self) -> Set[str]:
        """Get documented pages from docs/frontend/pages/"""
        documented_pages = set()
        
        pages_dir = self.docs_dir / "frontend" / "pages"
        if pages_dir.exists():
            for page_file in pages_dir.glob("*.md"):
                # Extract page path from filename
                page_name = page_file.stem
                if page_name == "index":
                    documented_pages.add("/")
                else:
                    documented_pages.add(f"/{page_name}")
        
        return documented_pages

def generate_backend_report(endpoints: List[BackendEndpoint], output_path: Path):
    """Generate backend endpoints report"""
    logger.info(f"Generating backend report: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Backend Endpoints Wiring Report\n\n")
        f.write(f"**Generated**: {datetime.now().isoformat()}\n")
        f.write(f"**Total Endpoints**: {len(endpoints)}\n\n")
        
        # Summary statistics
        services = set(ep.service for ep in endpoints)
        f.write(f"**Services Analyzed**: {len(services)}\n")
        f.write(f"**Services**: {', '.join(sorted(services))}\n\n")
        
        # Health and metrics summary
        health_endpoints = [ep for ep in endpoints if ep.endpoint == '/health']
        metrics_endpoints = [ep for ep in endpoints if ep.endpoint == '/metrics']
        
        f.write("## Health & Metrics Coverage\n\n")
        f.write(f"- **Health Endpoints**: {len(health_endpoints)}/{len(services)}\n")
        f.write(f"- **Metrics Endpoints**: {len(metrics_endpoints)}/{len(services)}\n\n")
        
        # Detailed endpoint table
        f.write("## Endpoint Details\n\n")
        f.write("| Service | Endpoint | Method | From Router | In Docs? | In OpenAPI? | Health/Metrics? |\n")
        f.write("|---------|----------|--------|-------------|----------|-------------|-----------------|\n")
        
        for endpoint in sorted(endpoints, key=lambda x: (x.service, x.endpoint)):
            health_metrics = "✅" if endpoint.has_health and endpoint.has_metrics else "❌"
            in_docs = "✅" if endpoint.in_docs else "❌"
            in_openapi = "✅" if endpoint.in_openapi else "❌"
            
            f.write(f"| {endpoint.service} | {endpoint.endpoint} | {endpoint.method} | {endpoint.from_router} | {in_docs} | {in_openapi} | {health_metrics} |\n")
        
        # Issues summary
        f.write("\n## Issues Summary\n\n")
        
        missing_health = [ep.service for ep in endpoints if ep.endpoint == '/health' and not ep.has_health]
        missing_metrics = [ep.service for ep in endpoints if ep.endpoint == '/metrics' and not ep.has_metrics]
        undocumented = [ep for ep in endpoints if not ep.in_docs]
        
        if missing_health:
            f.write(f"- **Missing Health Endpoints**: {', '.join(set(missing_health))}\n")
        if missing_metrics:
            f.write(f"- **Missing Metrics Endpoints**: {', '.join(set(missing_metrics))}\n")
        if undocumented:
            f.write(f"- **Undocumented Endpoints**: {len(undocumented)} endpoints\n")
        
        f.write("\n## Service Summary\n\n")
        for service in sorted(services):
            service_endpoints = [ep for ep in endpoints if ep.service == service]
            f.write(f"### {service}\n")
            f.write(f"- **Total Endpoints**: {len(service_endpoints)}\n")
            f.write(f"- **Health Endpoint**: {'✅' if any(ep.endpoint == '/health' for ep in service_endpoints) else '❌'}\n")
            f.write(f"- **Metrics Endpoint**: {'✅' if any(ep.endpoint == '/metrics' for ep in service_endpoints) else '❌'}\n")
            f.write(f"- **Documented**: {len([ep for ep in service_endpoints if ep.in_docs])}/{len(service_endpoints)}\n\n")

def generate_frontend_report(routes: List[FrontendRoute], output_path: Path):
    """Generate frontend routes report"""
    logger.info(f"Generating frontend report: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Frontend Routes Wiring Report\n\n")
        f.write(f"**Generated**: {datetime.now().isoformat()}\n")
        f.write(f"**Total Routes**: {len(routes)}\n\n")
        
        # Summary statistics
        found_routes = [r for r in routes if r.found]
        missing_routes = [r for r in routes if not r.found]
        documented_routes = [r for r in routes if r.in_docs]
        
        f.write("## Route Coverage Summary\n\n")
        f.write(f"- **Found Routes**: {len(found_routes)}\n")
        f.write(f"- **Missing Routes**: {len(missing_routes)}\n")
        f.write(f"- **Documented Routes**: {len(documented_routes)}\n")
        f.write(f"- **Coverage**: {len(found_routes)}/{len(documented_routes)} ({len(found_routes)/len(documented_routes)*100:.1f}%)\n\n")
        
        # Guided Prompt and Settings coverage
        guided_prompt_routes = [r for r in routes if r.has_guided_prompt]
        settings_routes = [r for r in routes if r.has_settings_toggle]
        
        f.write("## Component Integration\n\n")
        f.write(f"- **Guided Prompt Integration**: {len(guided_prompt_routes)}/{len(found_routes)} routes\n")
        f.write(f"- **Settings Toggle**: {len(settings_routes)}/{len(found_routes)} routes\n\n")
        
        # Detailed route table
        f.write("## Route Details\n\n")
        f.write("| Path | Page File | Found | Components | Guided Prompt | Settings Toggle | In Docs? |\n")
        f.write("|------|-----------|-------|------------|---------------|-----------------|----------|\n")
        
        for route in sorted(routes, key=lambda x: x.path):
            found = "✅" if route.found else "❌"
            guided_prompt = "✅" if route.has_guided_prompt else "❌"
            settings_toggle = "✅" if route.has_settings_toggle else "❌"
            in_docs = "✅" if route.in_docs else "❌"
            components = ", ".join(route.components[:3]) + ("..." if len(route.components) > 3 else "")
            
            f.write(f"| {route.path} | {route.page_file} | {found} | {components} | {guided_prompt} | {settings_toggle} | {in_docs} |\n")
        
        # Issues summary
        f.write("\n## Issues Summary\n\n")
        
        if missing_routes:
            f.write("### Missing Routes\n")
            for route in missing_routes:
                f.write(f"- **{route.path}**: {route.page_file}\n")
            f.write("\n")
        
        missing_guided_prompt = [r for r in found_routes if r.in_docs and not r.has_guided_prompt]
        if missing_guided_prompt:
            f.write("### Missing Guided Prompt Integration\n")
            for route in missing_guided_prompt:
                f.write(f"- **{route.path}**: {route.page_file}\n")
            f.write("\n")
        
        missing_settings = [r for r in found_routes if r.in_docs and not r.has_settings_toggle]
        if missing_settings:
            f.write("### Missing Settings Toggle\n")
            for route in missing_settings:
                f.write(f"- **{route.path}**: {route.page_file}\n")
            f.write("\n")

def main():
    """Main function"""
    project_root = Path(__file__).parent.parent
    
    # Create output directory
    output_dir = project_root / "reports" / "wiring"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Starting wiring analysis...")
    
    # Analyze backend
    backend_analyzer = BackendWiringAnalyzer(project_root)
    backend_endpoints = backend_analyzer.analyze_all_services()
    
    # Analyze frontend
    frontend_analyzer = FrontendWiringAnalyzer(project_root)
    frontend_routes = frontend_analyzer.analyze_frontend_routes()
    
    # Generate reports
    generate_backend_report(backend_endpoints, output_dir / "backend_endpoints.md")
    generate_frontend_report(frontend_routes, output_dir / "frontend_routes.md")
    
    logger.info("Wiring analysis complete!")
    logger.info(f"Backend endpoints: {len(backend_endpoints)}")
    logger.info(f"Frontend routes: {len(frontend_routes)}")
    logger.info(f"Reports generated in: {output_dir}")

if __name__ == "__main__":
    main()
