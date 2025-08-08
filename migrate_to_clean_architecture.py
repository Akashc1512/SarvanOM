#!/usr/bin/env python3
"""
Migration Script for Clean Architecture Implementation

This script helps migrate the existing api_gateway service to the new clean architecture structure.
It analyzes the current codebase and provides guidance for the migration process.
"""

import os
import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MigrationItem:
    """Represents a migration item."""
    source_file: str
    target_location: str
    migration_type: str  # 'move', 'refactor', 'split', 'merge'
    priority: int  # 1-5, where 1 is highest priority
    description: str
    dependencies: List[str] = None

class CleanArchitectureMigrator:
    """Handles migration from monolithic to clean architecture."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.api_gateway_path = self.project_root / "services" / "api_gateway"
        self.backend_path = self.project_root / "backend"
        self.migration_items: List[MigrationItem] = []
        
    def analyze_current_structure(self) -> Dict[str, any]:
        """Analyze the current api_gateway structure."""
        analysis = {
            "files": {},
            "endpoints": [],
            "services": [],
            "models": [],
            "dependencies": set()
        }
        
        # Analyze main.py
        main_file = self.api_gateway_path / "main.py"
        if main_file.exists():
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()
                analysis["files"]["main.py"] = {
                    "size": len(content),
                    "lines": len(content.split('\n')),
                    "endpoints": self._extract_endpoints(content),
                    "imports": self._extract_imports(content)
                }
        
        # Analyze routes
        routes_path = self.api_gateway_path / "routes"
        if routes_path.exists():
            for route_file in routes_path.glob("*.py"):
                if route_file.name != "__init__.py":
                    with open(route_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        analysis["files"][f"routes/{route_file.name}"] = {
                            "size": len(content),
                            "lines": len(content.split('\n')),
                            "endpoints": self._extract_endpoints(content),
                            "imports": self._extract_imports(content)
                        }
        
        # Analyze services
        services_path = self.api_gateway_path / "services"
        if services_path.exists():
            for service_file in services_path.glob("*.py"):
                if service_file.name != "__init__.py":
                    with open(service_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        analysis["files"][f"services/{service_file.name}"] = {
                            "size": len(content),
                            "lines": len(content.split('\n')),
                            "classes": self._extract_classes(content),
                            "imports": self._extract_imports(content)
                        }
        
        return analysis
    
    def _extract_endpoints(self, content: str) -> List[str]:
        """Extract endpoint definitions from FastAPI code."""
        endpoints = []
        # Look for @router.post, @router.get, etc.
        patterns = [
            r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
            r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for method, path in matches:
                endpoints.append(f"{method.upper()} {path}")
        
        return endpoints
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements from code."""
        imports = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)
        
        return imports
    
    def _extract_classes(self, content: str) -> List[str]:
        """Extract class definitions from code."""
        classes = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('class ') and ':' in line:
                class_name = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                classes.append(class_name)
        
        return classes
    
    def generate_migration_plan(self, analysis: Dict[str, any]) -> List[MigrationItem]:
        """Generate a migration plan based on analysis."""
        plan = []
        
        # High priority: Core services
        if "services/query_service.py" in analysis["files"]:
            plan.append(MigrationItem(
                source_file="services/api_gateway/services/query_service.py",
                target_location="backend/services/query/query_processor.py",
                migration_type="refactor",
                priority=1,
                description="Migrate QueryService to QueryProcessor in clean architecture",
                dependencies=[]
            ))
        
        # High priority: Main application
        if "main.py" in analysis["files"]:
            plan.append(MigrationItem(
                source_file="services/api_gateway/main.py",
                target_location="backend/main.py",
                migration_type="refactor",
                priority=1,
                description="Migrate main FastAPI app to clean architecture",
                dependencies=[]
            ))
        
        # High priority: Query routes
        if "routes/queries.py" in analysis["files"]:
            plan.append(MigrationItem(
                source_file="services/api_gateway/routes/queries.py",
                target_location="backend/api/routers/query_router.py",
                migration_type="refactor",
                priority=1,
                description="Migrate query endpoints to clean architecture router",
                dependencies=["backend/services/query/query_processor.py"]
            ))
        
        # Medium priority: Health service
        if "services/health_service.py" in analysis["files"]:
            plan.append(MigrationItem(
                source_file="services/api_gateway/services/health_service.py",
                target_location="backend/services/health/health_service.py",
                migration_type="refactor",
                priority=2,
                description="Migrate health service to clean architecture",
                dependencies=[]
            ))
        
        # Medium priority: Health routes
        if "routes/health.py" in analysis["files"]:
            plan.append(MigrationItem(
                source_file="services/api_gateway/routes/health.py",
                target_location="backend/api/routers/health_router.py",
                migration_type="refactor",
                priority=2,
                description="Migrate health endpoints to clean architecture router",
                dependencies=["backend/services/health/health_service.py"]
            ))
        
        # Medium priority: Agent services
        if "routes/agents.py" in analysis["files"] or "routes/agents_new.py" in analysis["files"]:
            plan.append(MigrationItem(
                source_file="services/api_gateway/routes/agents.py",
                target_location="backend/api/routers/agent_router.py",
                migration_type="refactor",
                priority=2,
                description="Migrate agent endpoints to clean architecture router",
                dependencies=["backend/services/agents/agent_coordinator.py"]
            ))
        
        # Low priority: Other services
        other_services = [
            "database_service.py",
            "knowledge_service.py",
            "pdf_service.py",
            "crawler_service.py",
            "code_service.py",
            "browser_service.py"
        ]
        
        for service in other_services:
            if f"services/{service}" in analysis["files"]:
                plan.append(MigrationItem(
                    source_file=f"services/api_gateway/services/{service}",
                    target_location=f"backend/services/core/{service.replace('_service.py', '_service.py')}",
                    migration_type="refactor",
                    priority=3,
                    description=f"Migrate {service} to clean architecture",
                    dependencies=[]
                ))
        
        return plan
    
    def print_migration_plan(self, plan: List[MigrationItem]):
        """Print the migration plan in a readable format."""
        print("=" * 80)
        print("CLEAN ARCHITECTURE MIGRATION PLAN")
        print("=" * 80)
        print(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Group by priority
        priority_groups = {}
        for item in plan:
            if item.priority not in priority_groups:
                priority_groups[item.priority] = []
            priority_groups[item.priority].append(item)
        
        for priority in sorted(priority_groups.keys()):
            print(f"PRIORITY {priority} (Highest Priority = 1)")
            print("-" * 40)
            
            for item in priority_groups[priority]:
                print(f"• {item.description}")
                print(f"  Source: {item.source_file}")
                print(f"  Target: {item.target_location}")
                print(f"  Type: {item.migration_type}")
                if item.dependencies:
                    print(f"  Dependencies: {', '.join(item.dependencies)}")
                print()
        
        print("=" * 80)
        print("MIGRATION STEPS:")
        print("1. Start with Priority 1 items (core services)")
        print("2. Move to Priority 2 items (supporting services)")
        print("3. Complete with Priority 3 items (utility services)")
        print("4. Test each migration step")
        print("5. Update imports and dependencies")
        print("=" * 80)

def main():
    """Main migration analysis function."""
    migrator = CleanArchitectureMigrator()
    
    print("Analyzing current api_gateway structure...")
    analysis = migrator.analyze_current_structure()
    
    print("Generating migration plan...")
    plan = migrator.generate_migration_plan(analysis)
    
    print("Current Structure Analysis:")
    print(f"- Total files analyzed: {len(analysis['files'])}")
    print(f"- Total endpoints found: {sum(len(f.get('endpoints', [])) for f in analysis['files'].values())}")
    print(f"- Total classes found: {sum(len(f.get('classes', [])) for f in analysis['files'].values())}")
    print()
    
    migrator.print_migration_plan(plan)
    
    # Save analysis to file
    with open("migration_analysis.json", "w") as f:
        import json
        # Convert sets to lists for JSON serialization
        analysis_serializable = analysis.copy()
        analysis_serializable["dependencies"] = list(analysis["dependencies"])
        json.dump(analysis_serializable, f, indent=2)
    
    print("Analysis saved to migration_analysis.json")

if __name__ == "__main__":
    main() 