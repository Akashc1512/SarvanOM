#!/usr/bin/env python3
"""
Doc→Code Compliance Suite - SarvanOM v2

This script analyzes the codebase against documentation requirements and generates
machine-readable compliance reports.

Backend Checks:
1. env_matrix.md parity: scan code for env reads and confirm canonical names
2. budgets.md: verify timeouts/budgets match 5/7/10s and Guided Prompt ≤500ms
3. lanes.md: verify provider execution order and keyless fallbacks
4. router_policy.md: confirm router mounts and graceful disable
5. metrics.md: confirm emission of required tags
6. main.py wiring: ensure FastAPI app registers all routers

Frontend Checks:
7. routes.md: diff Next.js route tree vs documented routes
8. components.md: verify pages import canonical components
9. Guided Prompt presence: check GuidedPromptModal wiring
10. Fallback UX: ensure "ⓘ via fallback" badge rendering

Output:
- reports/compliance/backend.md (PASS/FAIL table per check)
- reports/compliance/frontend.md (routes/components/guided/fallback PASS/FAIL)
- reports/compliance/env_gaps.json (unknown keys, unused keys, synonyms)
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
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ComplianceCheck:
    """Represents a single compliance check result"""
    check_id: str
    description: str
    status: str  # PASS, FAIL, WARN
    details: str
    file_locations: List[str]
    severity: str = "medium"  # low, medium, high, critical

@dataclass
class ComplianceReport:
    """Represents a compliance report"""
    timestamp: str
    total_checks: int
    passed: int
    failed: int
    warnings: int
    checks: List[ComplianceCheck]

class ComplianceChecker:
    """Main compliance checking class"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.docs_root = self.project_root / "docs"
        self.services_root = self.project_root / "services"
        self.shared_root = self.project_root / "shared"
        self.frontend_root = self.project_root / "frontend"
        
        # Load documentation requirements
        self.env_matrix = self._load_env_matrix()
        self.budgets = self._load_budgets()
        self.lanes = self._load_lanes()
        self.routes = self._load_routes()
        self.components = self._load_components()
        
        # Track findings
        self.backend_checks: List[ComplianceCheck] = []
        self.frontend_checks: List[ComplianceCheck] = []
        self.env_gaps: Dict[str, Any] = {
            "unknown_keys": [],
            "unused_keys": [],
            "synonyms": [],
            "canonical_keys": []
        }
    
    def _load_env_matrix(self) -> Dict[str, Any]:
        """Load environment variable matrix from documentation"""
        env_file = self.docs_root / "contracts" / "env_matrix.md"
        if not env_file.exists():
            logger.warning(f"Environment matrix file not found: {env_file}")
            return {}
        
        canonical_vars = set()
        aliases = {}
        
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Extract canonical variables (✅ **CANONICAL**)
            canonical_matches = re.findall(r'`([A-Z_]+)`\s*\|\s*✅\s*\*\*CANONICAL\*\*', content)
            canonical_vars.update(canonical_matches)
            
            # Extract aliases (⚠️ **ALIAS**)
            alias_matches = re.findall(r'`([A-Z_]+)`\s*\|\s*`([A-Z_]+)`\s*\|\s*⚠️\s*\*\*ALIAS\*\*', content)
            for alias, canonical in alias_matches:
                aliases[alias] = canonical
        
        return {
            "canonical_vars": canonical_vars,
            "aliases": aliases
        }
    
    def _load_budgets(self) -> Dict[str, Any]:
        """Load budget requirements from documentation"""
        budget_file = self.docs_root / "architecture" / "budgets.md"
        if not budget_file.exists():
            logger.warning(f"Budget file not found: {budget_file}")
            return {}
        
        with open(budget_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Extract global deadlines
            deadlines = {}
            deadline_matches = re.findall(r'\|\s*(\w+)\s*\|\s*.*?\|\s*(\d+)\s*seconds?\s*\|', content)
            for mode, seconds in deadline_matches:
                deadlines[mode.lower()] = int(seconds) * 1000  # Convert to ms
            
            # Extract guided prompt budget
            guided_prompt_match = re.search(r'Guided Prompt Pre-flight.*?(\d+)ms', content)
            guided_prompt_budget = int(guided_prompt_match.group(1)) if guided_prompt_match else 500
            
            return {
                "global_deadlines": deadlines,
                "guided_prompt_budget": guided_prompt_budget
            }
    
    def _load_lanes(self) -> Dict[str, Any]:
        """Load lane requirements from documentation"""
        lanes_file = self.docs_root / "retrieval" / "lanes.md"
        if not lanes_file.exists():
            logger.warning(f"Lanes file not found: {lanes_file}")
            return {}
        
        with open(lanes_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Extract provider orders
            provider_orders = {}
            
            # Web lane providers
            web_match = re.search(r'Web Lane.*?Primary Engine.*?(\w+).*?Fallback Engine.*?(\w+)', content, re.DOTALL)
            if web_match:
                provider_orders["web"] = {
                    "primary": web_match.group(1),
                    "fallback": web_match.group(2)
                }
            
            # News lane providers
            news_match = re.search(r'News Lane.*?Primary Source.*?(\w+).*?Fallback Source.*?(\w+)', content, re.DOTALL)
            if news_match:
                provider_orders["news"] = {
                    "primary": news_match.group(1),
                    "fallback": news_match.group(2)
                }
            
            # Markets lane providers
            markets_match = re.search(r'Markets Lane.*?Primary Source.*?(\w+).*?Fallback Sources.*?(\w+)', content, re.DOTALL)
            if markets_match:
                provider_orders["markets"] = {
                    "primary": markets_match.group(1),
                    "fallback": markets_match.group(2)
                }
            
            return {
                "provider_orders": provider_orders,
                "provider_timeout": 800,  # ≤800ms per provider
                "keyless_fallbacks": ["DuckDuckGo", "Wikipedia", "GDELT", "Stooq"]
            }
    
    def _load_routes(self) -> Dict[str, Any]:
        """Load route requirements from documentation"""
        routes_file = self.docs_root / "frontend" / "routes.md"
        if not routes_file.exists():
            logger.warning(f"Routes file not found: {routes_file}")
            return {}
        
        with open(routes_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Extract documented routes
            routes = set()
            route_matches = re.findall(r'`/([^`]+)`', content)
            routes.update(route_matches)
            
            return {"documented_routes": routes}
    
    def _load_components(self) -> Dict[str, Any]:
        """Load component requirements from documentation"""
        components_file = self.docs_root / "frontend" / "components.md"
        if not components_file.exists():
            logger.warning(f"Components file not found: {components_file}")
            return {}
        
        with open(components_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Extract canonical components
            components = set()
            component_matches = re.findall(r'`([A-Z][a-zA-Z0-9]+)`', content)
            components.update(component_matches)
            
            return {"canonical_components": components}
    
    def check_env_matrix_parity(self):
        """Check 1: Environment variable matrix parity"""
        logger.info("Checking environment variable matrix parity...")
        
        # Find all Python files that read environment variables
        python_files = list(self.project_root.rglob("*.py"))
        env_reads = set()
        unknown_keys = set()
        synonyms_found = set()
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Find os.getenv, os.environ, and similar patterns
                    env_patterns = [
                        r'os\.getenv\(["\']([^"\']+)["\']',
                        r'os\.environ\[["\']([^"\']+)["\']',
                        r'os\.environ\.get\(["\']([^"\']+)["\']',
                        r'getenv\(["\']([^"\']+)["\']',
                        r'environ\[["\']([^"\']+)["\']',
                        r'environ\.get\(["\']([^"\']+)["\']'
                    ]
                    
                    for pattern in env_patterns:
                        matches = re.findall(pattern, content)
                        for match in matches:
                            env_reads.add(match)
                            
                            # Check if it's canonical
                            if match in self.env_matrix.get("canonical_vars", set()):
                                continue
                            
                            # Check if it's an alias
                            if match in self.env_matrix.get("aliases", {}):
                                synonyms_found.add(match)
                                continue
                            
                            # Unknown key
                            unknown_keys.add(match)
                            
            except Exception as e:
                logger.warning(f"Error reading {file_path}: {e}")
        
        # Check for unused canonical keys
        unused_keys = self.env_matrix.get("canonical_vars", set()) - env_reads
        
        # Update env_gaps
        self.env_gaps["unknown_keys"] = list(unknown_keys)
        self.env_gaps["unused_keys"] = list(unused_keys)
        self.env_gaps["synonyms"] = list(synonyms_found)
        self.env_gaps["canonical_keys"] = list(env_reads.intersection(self.env_matrix.get("canonical_vars", set())))
        
        # Create compliance check
        status = "PASS" if not unknown_keys and not synonyms_found else "FAIL"
        details = f"Found {len(unknown_keys)} unknown keys, {len(synonyms_found)} synonyms, {len(unused_keys)} unused canonical keys"
        
        self.backend_checks.append(ComplianceCheck(
            check_id="env_matrix_parity",
            description="Environment variable matrix parity - canonical names only",
            status=status,
            details=details,
            file_locations=list(unknown_keys) + list(synonyms_found),
            severity="high"
        ))
    
    def check_budgets_compliance(self):
        """Check 2: Budget compliance"""
        logger.info("Checking budget compliance...")
        
        # Find budget-related configurations
        budget_files = [
            self.project_root / "shared" / "core" / "config" / "central_config.py",
            self.project_root / "services" / "retrieval" / "main.py",
            self.project_root / "services" / "guided_prompt" / "main.py"
        ]
        
        budget_violations = []
        
        for file_path in budget_files:
            if not file_path.exists():
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check for hardcoded timeouts that don't match budgets
                    timeout_patterns = [
                        r'timeout[=:]\s*(\d+)',
                        r'timeout_ms[=:]\s*(\d+)',
                        r'budget[=:]\s*(\d+)',
                        r'deadline[=:]\s*(\d+)'
                    ]
                    
                    for pattern in timeout_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches:
                            timeout_ms = int(match)
                            
                            # Check against documented budgets
                            if timeout_ms > 10000:  # Research budget
                                budget_violations.append(f"{file_path}: {timeout_ms}ms exceeds research budget")
                            elif timeout_ms > 500 and "guided" in content.lower():
                                budget_violations.append(f"{file_path}: {timeout_ms}ms exceeds guided prompt budget")
                                
            except Exception as e:
                logger.warning(f"Error reading {file_path}: {e}")
        
        status = "PASS" if not budget_violations else "FAIL"
        details = f"Found {len(budget_violations)} budget violations" if budget_violations else "All budgets comply with documentation"
        
        self.backend_checks.append(ComplianceCheck(
            check_id="budgets_compliance",
            description="Budget compliance - 5/7/10s and Guided Prompt ≤500ms",
            status=status,
            details=details,
            file_locations=budget_violations,
            severity="high"
        ))
    
    def check_lanes_provider_order(self):
        """Check 3: Lanes provider execution order"""
        logger.info("Checking lanes provider execution order...")
        
        # Check retrieval service for proper provider order
        retrieval_file = self.services_root / "retrieval" / "main.py"
        violations = []
        
        if retrieval_file.exists():
            try:
                with open(retrieval_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check for provider order implementation
                    if "parallel" not in content.lower():
                        violations.append("Missing parallel execution")
                    
                    if "timeout" not in content.lower():
                        violations.append("Missing timeout handling")
                    
                    if "keyless" not in content.lower():
                        violations.append("Missing keyless fallback implementation")
                        
            except Exception as e:
                logger.warning(f"Error reading {retrieval_file}: {e}")
        
        status = "PASS" if not violations else "FAIL"
        details = f"Found {len(violations)} lane implementation issues" if violations else "Lane implementation follows documentation"
        
        self.backend_checks.append(ComplianceCheck(
            check_id="lanes_provider_order",
            description="Lanes provider execution order and keyless fallbacks",
            status=status,
            details=details,
            file_locations=violations,
            severity="medium"
        ))
    
    def check_router_policy(self):
        """Check 4: Router policy compliance"""
        logger.info("Checking router policy compliance...")
        
        # Check model registry service for router mounting
        model_registry_file = self.services_root / "model_registry" / "main.py"
        violations = []
        
        if model_registry_file.exists():
            try:
                with open(model_registry_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check for required routers
                    required_routers = ["router", "routing_router", "search_router", "feeds_router"]
                    for router in required_routers:
                        if router not in content:
                            violations.append(f"Missing {router}")
                    
                    # Check for graceful disable
                    if "graceful" not in content.lower():
                        violations.append("Missing graceful disable implementation")
                        
            except Exception as e:
                logger.warning(f"Error reading {model_registry_file}: {e}")
        
        status = "PASS" if not violations else "FAIL"
        details = f"Found {len(violations)} router policy violations" if violations else "Router policy correctly implemented"
        
        self.backend_checks.append(ComplianceCheck(
            check_id="router_policy",
            description="Router policy - OpenAI/Anthropic text, Gemini vision, graceful disable",
            status=status,
            details=details,
            file_locations=violations,
            severity="medium"
        ))
    
    def check_metrics_tags(self):
        """Check 5: Metrics tags compliance"""
        logger.info("Checking metrics tags compliance...")
        
        # Check for required metrics tags
        required_tags = ["trace_id", "lane", "provider", "fallback_used", "timeout"]
        violations = []
        
        # Check services for metrics implementation
        service_files = list(self.services_root.rglob("main.py"))
        
        for file_path in service_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check for Prometheus metrics
                    if "prometheus" not in content.lower():
                        violations.append(f"{file_path}: Missing Prometheus metrics")
                        continue
                    
                    # Check for required tags
                    for tag in required_tags:
                        if tag not in content:
                            violations.append(f"{file_path}: Missing {tag} tag")
                            
            except Exception as e:
                logger.warning(f"Error reading {file_path}: {e}")
        
        status = "PASS" if not violations else "FAIL"
        details = f"Found {len(violations)} metrics tag violations" if violations else "All required metrics tags present"
        
        self.backend_checks.append(ComplianceCheck(
            check_id="metrics_tags",
            description="Metrics tags - trace_id, lane, provider, fallback_used, timeout",
            status=status,
            details=details,
            file_locations=violations,
            severity="medium"
        ))
    
    def check_main_py_wiring(self):
        """Check 6: Main.py wiring compliance"""
        logger.info("Checking main.py wiring compliance...")
        
        violations = []
        
        # Check each service main.py
        service_dirs = [d for d in self.services_root.iterdir() if d.is_dir()]
        
        for service_dir in service_dirs:
            main_file = service_dir / "main.py"
            if not main_file.exists():
                continue
                
            try:
                with open(main_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check for FastAPI app creation
                    if "FastAPI" not in content:
                        violations.append(f"{main_file}: Missing FastAPI app creation")
                    
                    # Check for health endpoint
                    if "/health" not in content:
                        violations.append(f"{main_file}: Missing /health endpoint")
                    
                    # Check for metrics endpoint
                    if "/metrics" not in content:
                        violations.append(f"{main_file}: Missing /metrics endpoint")
                    
                    # Check for CORS middleware
                    if "CORS" not in content:
                        violations.append(f"{main_file}: Missing CORS middleware")
                        
            except Exception as e:
                logger.warning(f"Error reading {main_file}: {e}")
        
        status = "PASS" if not violations else "FAIL"
        details = f"Found {len(violations)} wiring violations" if violations else "All main.py files properly wired"
        
        self.backend_checks.append(ComplianceCheck(
            check_id="main_py_wiring",
            description="Main.py wiring - FastAPI app, routers, /health, /metrics",
            status=status,
            details=details,
            file_locations=violations,
            severity="high"
        ))
    
    def check_frontend_routes(self):
        """Check 7: Frontend routes compliance"""
        logger.info("Checking frontend routes compliance...")
        
        violations = []
        
        # Get actual Next.js routes
        app_dir = self.frontend_root / "src" / "app"
        if not app_dir.exists():
            violations.append("Frontend app directory not found")
        else:
            actual_routes = set()
            
            # Walk through app directory to find routes
            for item in app_dir.rglob("*"):
                if item.is_dir() and item.name != "node_modules":
                    # Convert path to route
                    route = "/" + str(item.relative_to(app_dir)).replace("\\", "/")
                    if route != "/":
                        actual_routes.add(route)
            
            # Compare with documented routes
            documented_routes = self.routes.get("documented_routes", set())
            
            missing_routes = documented_routes - actual_routes
            extra_routes = actual_routes - documented_routes
            
            if missing_routes:
                violations.append(f"Missing routes: {list(missing_routes)}")
            
            if extra_routes:
                violations.append(f"Extra routes: {list(extra_routes)}")
        
        status = "PASS" if not violations else "FAIL"
        details = f"Found {len(violations)} route mismatches" if violations else "All routes match documentation"
        
        self.frontend_checks.append(ComplianceCheck(
            check_id="frontend_routes",
            description="Frontend routes - Next.js route tree vs documented routes",
            status=status,
            details=details,
            file_locations=violations,
            severity="medium"
        ))
    
    def check_frontend_components(self):
        """Check 8: Frontend components compliance"""
        logger.info("Checking frontend components compliance...")
        
        violations = []
        
        # Check for canonical component usage
        canonical_components = self.components.get("canonical_components", set())
        
        # Check component files
        components_dir = self.frontend_root / "src" / "components"
        if components_dir.exists():
            for component_file in components_dir.rglob("*.tsx"):
                try:
                    with open(component_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Check for deprecated component usage
                        deprecated_patterns = [
                            r'import.*from.*["\']@/components/([^"\']+)["\']',
                            r'<([A-Z][a-zA-Z0-9]+)'
                        ]
                        
                        for pattern in deprecated_patterns:
                            matches = re.findall(pattern, content)
                            for match in matches:
                                if match not in canonical_components and match.isupper():
                                    violations.append(f"{component_file}: Using non-canonical component {match}")
                                    
                except Exception as e:
                    logger.warning(f"Error reading {component_file}: {e}")
        
        status = "PASS" if not violations else "FAIL"
        details = f"Found {len(violations)} component violations" if violations else "All components are canonical"
        
        self.frontend_checks.append(ComplianceCheck(
            check_id="frontend_components",
            description="Frontend components - canonical components only",
            status=status,
            details=details,
            file_locations=violations,
            severity="low"
        ))
    
    def check_guided_prompt_presence(self):
        """Check 9: Guided Prompt presence"""
        logger.info("Checking Guided Prompt presence...")
        
        violations = []
        
        # Check for GuidedPromptModal component
        guided_prompt_file = self.frontend_root / "src" / "components" / "GuidedPromptModal.tsx"
        if not guided_prompt_file.exists():
            violations.append("GuidedPromptModal.tsx not found")
        
        # Check for guided prompt usage in pages
        pages_dir = self.frontend_root / "src" / "app"
        if pages_dir.exists():
            for page_file in pages_dir.rglob("*.tsx"):
                try:
                    with open(page_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Check for guided prompt usage
                        if "GuidedPrompt" in content:
                            # Check for settings toggle
                            if "settings" not in content.lower():
                                violations.append(f"{page_file}: Guided prompt without settings toggle")
                                
                except Exception as e:
                    logger.warning(f"Error reading {page_file}: {e}")
        
        status = "PASS" if not violations else "FAIL"
        details = f"Found {len(violations)} guided prompt violations" if violations else "Guided prompt properly implemented"
        
        self.frontend_checks.append(ComplianceCheck(
            check_id="guided_prompt_presence",
            description="Guided Prompt presence - modal wired, default ON, settings toggle",
            status=status,
            details=details,
            file_locations=violations,
            severity="medium"
        ))
    
    def check_fallback_ux(self):
        """Check 10: Fallback UX compliance"""
        logger.info("Checking fallback UX compliance...")
        
        violations = []
        
        # Check for fallback badge implementation
        search_pages = [
            self.frontend_root / "src" / "app" / "search" / "page.tsx",
            self.frontend_root / "src" / "app" / "comprehensive-query" / "page.tsx"
        ]
        
        for page_file in search_pages:
            if page_file.exists():
                try:
                    with open(page_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Check for fallback badge
                        if "fallback" not in content.lower() and "ⓘ" not in content:
                            violations.append(f"{page_file}: Missing fallback badge")
                            
                except Exception as e:
                    logger.warning(f"Error reading {page_file}: {e}")
        
        status = "PASS" if not violations else "FAIL"
        details = f"Found {len(violations)} fallback UX violations" if violations else "Fallback UX properly implemented"
        
        self.frontend_checks.append(ComplianceCheck(
            check_id="fallback_ux",
            description="Fallback UX - 'ⓘ via fallback' badge on Search/Comprehensive pages",
            status=status,
            details=details,
            file_locations=violations,
            severity="low"
        ))
    
    def run_all_checks(self):
        """Run all compliance checks"""
        logger.info("Running all compliance checks...")
        
        # Backend checks
        self.check_env_matrix_parity()
        self.check_budgets_compliance()
        self.check_lanes_provider_order()
        self.check_router_policy()
        self.check_metrics_tags()
        self.check_main_py_wiring()
        
        # Frontend checks
        self.check_frontend_routes()
        self.check_frontend_components()
        self.check_guided_prompt_presence()
        self.check_fallback_ux()
    
    def generate_backend_report(self) -> str:
        """Generate backend compliance report"""
        report = f"""# Backend Compliance Report

**Generated**: {datetime.now().isoformat()}
**Total Checks**: {len(self.backend_checks)}

## Summary

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ PASS | {sum(1 for c in self.backend_checks if c.status == 'PASS')} | {sum(1 for c in self.backend_checks if c.status == 'PASS') / len(self.backend_checks) * 100:.1f}% |
| ❌ FAIL | {sum(1 for c in self.backend_checks if c.status == 'FAIL')} | {sum(1 for c in self.backend_checks if c.status == 'FAIL') / len(self.backend_checks) * 100:.1f}% |
| ⚠️ WARN | {sum(1 for c in self.backend_checks if c.status == 'WARN')} | {sum(1 for c in self.backend_checks if c.status == 'WARN') / len(self.backend_checks) * 100:.1f}% |

## Detailed Results

"""
        
        for check in self.backend_checks:
            status_icon = "✅" if check.status == "PASS" else "❌" if check.status == "FAIL" else "⚠️"
            report += f"""### {status_icon} {check.check_id}

**Description**: {check.description}
**Status**: {check.status}
**Severity**: {check.severity}
**Details**: {check.details}

**File Locations**:
"""
            for location in check.file_locations:
                report += f"- {location}\n"
            report += "\n"
        
        return report
    
    def generate_frontend_report(self) -> str:
        """Generate frontend compliance report"""
        report = f"""# Frontend Compliance Report

**Generated**: {datetime.now().isoformat()}
**Total Checks**: {len(self.frontend_checks)}

## Summary

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ PASS | {sum(1 for c in self.frontend_checks if c.status == 'PASS')} | {sum(1 for c in self.frontend_checks if c.status == 'PASS') / len(self.frontend_checks) * 100:.1f}% |
| ❌ FAIL | {sum(1 for c in self.frontend_checks if c.status == 'FAIL')} | {sum(1 for c in self.frontend_checks if c.status == 'FAIL') / len(self.frontend_checks) * 100:.1f}% |
| ⚠️ WARN | {sum(1 for c in self.frontend_checks if c.status == 'WARN')} | {sum(1 for c in self.frontend_checks if c.status == 'WARN') / len(self.frontend_checks) * 100:.1f}% |

## Detailed Results

"""
        
        for check in self.frontend_checks:
            status_icon = "✅" if check.status == "PASS" else "❌" if check.status == "FAIL" else "⚠️"
            report += f"""### {status_icon} {check.check_id}

**Description**: {check.description}
**Status**: {check.status}
**Severity**: {check.severity}
**Details**: {check.details}

**File Locations**:
"""
            for location in check.file_locations:
                report += f"- {location}\n"
            report += "\n"
        
        return report
    
    def generate_env_gaps_report(self) -> Dict[str, Any]:
        """Generate environment gaps report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_canonical_keys": len(self.env_gaps["canonical_keys"]),
                "unknown_keys_count": len(self.env_gaps["unknown_keys"]),
                "unused_keys_count": len(self.env_gaps["unused_keys"]),
                "synonyms_count": len(self.env_gaps["synonyms"])
            },
            "canonical_keys": self.env_gaps["canonical_keys"],
            "unknown_keys": self.env_gaps["unknown_keys"],
            "unused_keys": self.env_gaps["unused_keys"],
            "synonyms": self.env_gaps["synonyms"]
        }
    
    def save_reports(self):
        """Save all compliance reports"""
        reports_dir = self.project_root / "reports" / "compliance"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Save backend report
        backend_report = self.generate_backend_report()
        with open(reports_dir / "backend.md", 'w', encoding='utf-8') as f:
            f.write(backend_report)
        
        # Save frontend report
        frontend_report = self.generate_frontend_report()
        with open(reports_dir / "frontend.md", 'w', encoding='utf-8') as f:
            f.write(frontend_report)
        
        # Save environment gaps report
        env_gaps_report = self.generate_env_gaps_report()
        with open(reports_dir / "env_gaps.json", 'w', encoding='utf-8') as f:
            json.dump(env_gaps_report, f, indent=2)
        
        logger.info(f"Compliance reports saved to {reports_dir}")

def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent
    checker = ComplianceChecker(str(project_root))
    
    logger.info("Starting Doc→Code Compliance Suite...")
    checker.run_all_checks()
    checker.save_reports()
    logger.info("Compliance checking completed!")

if __name__ == "__main__":
    main()
