#!/usr/bin/env python3
"""
Comprehensive Setup Script for SarvanOM Project
Fixes all identified issues and sets up the project according to MAANG standards.

This script:
1. Fixes missing dependencies
2. Sets up environment variables
3. Fixes import path issues
4. Validates project structure
5. Sets up development environment
6. Runs health checks

Usage:
    python scripts/setup_comprehensive.py
"""

import os
import sys
import subprocess
import shutil
import re
from pathlib import Path
from typing import List, Dict, Any
import json

class SarvanOMSetup:
    """Comprehensive setup for SarvanOM project."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.issues_found = []
        self.fixes_applied = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def run_command(self, command: List[str], cwd: str = None) -> bool:
        """Run a command and return success status."""
        try:
            result = subprocess.run(
                command,
                cwd=cwd or str(self.project_root),
                capture_output=True,
                text=True,
                check=True
            )
            self.log(f"Command successful: {' '.join(command)}")
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {' '.join(command)}", "ERROR")
            self.log(f"Error: {e.stderr}", "ERROR")
            return False
    
    def fix_missing_dependencies(self):
        """Fix missing dependencies."""
        self.log("Fixing missing dependencies...")
        
        # Install concurrently globally
        if not self.run_command(["npm", "install", "-g", "concurrently"]):
            self.issues_found.append("Failed to install concurrently globally")
        
        # Install project dependencies
        if not self.run_command(["npm", "install"]):
            self.issues_found.append("Failed to install npm dependencies")
        
        # Install Python dependencies
        if not self.run_command([sys.executable, "-m", "pip", "install", "-e", ".", "[dev,test,security]"]):
            self.issues_found.append("Failed to install Python dependencies")
        
        self.fixes_applied.append("Dependencies installed")
    
    def setup_environment(self):
        """Set up environment variables."""
        self.log("Setting up environment variables...")
        
        env_template = self.project_root / "env.template"
        env_file = self.project_root / ".env"
        
        if not env_file.exists():
            if env_template.exists():
                shutil.copy(env_template, env_file)
                self.log("Created .env file from template")
            else:
                self.log("env.template not found, creating basic .env", "WARNING")
                self.create_basic_env()
        
        self.fixes_applied.append("Environment variables configured")
    
    def create_basic_env(self):
        """Create a basic .env file."""
        env_content = """# Basic environment configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
SERVICE_NAME=sarvanom-api
VERSION=1.0.0

# Server configuration
HOST=0.0.0.0
PORT=8000

# Security (CHANGE THESE IN PRODUCTION)
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here_change_in_production

# AI Configuration
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database (configure as needed)
DATABASE_URL=sqlite:///./sarvanom.db
REDIS_URL=redis://localhost:6379

# Development settings
MOCK_AI_RESPONSES=true
SKIP_AUTHENTICATION=false
"""
        
        with open(self.project_root / ".env", "w") as f:
            f.write(env_content)
    
    def fix_import_paths(self):
        """Fix inconsistent import paths."""
        self.log("Fixing import path issues...")
        
        # Files with auth-service imports
        files_to_fix = [
            "services/api_gateway/main.py",
            "services/api_gateway/endpoints_v1.py",
            "services/api_gateway/endpoints_v2.py",
            "services/api_gateway/v2/auth.py",
            "services/auth_service/auth_endpoints.py",
            "services/auth_service/auth.py",
            "services/analytics_service/integration_layer.py",
            "scripts/initialize_users.py"
        ]
        
        for file_path in files_to_fix:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.fix_file_imports(full_path)
        
        self.fixes_applied.append("Import paths standardized")
    
    def fix_file_imports(self, file_path: Path):
        """Fix import paths in a specific file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace auth-service with auth_service
            original_content = content
            content = re.sub(
                r'services\.auth-service',
                'services.auth_service',
                content
            )
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log(f"Fixed imports in {file_path}")
        
        except Exception as e:
            self.log(f"Failed to fix imports in {file_path}: {e}", "ERROR")
    
    def validate_project_structure(self):
        """Validate project structure."""
        self.log("Validating project structure...")
        
        required_dirs = [
            "services",
            "shared",
            "frontend",
            "tests",
            "scripts",
            "infrastructure"
        ]
        
        required_files = [
            "pyproject.toml",
            "package.json",
            "README.md",
            "env.template"
        ]
        
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                self.issues_found.append(f"Missing directory: {dir_name}")
            else:
                self.log(f"✓ Directory exists: {dir_name}")
        
        for file_name in required_files:
            file_path = self.project_root / file_name
            if not file_path.exists():
                self.issues_found.append(f"Missing file: {file_name}")
            else:
                self.log(f"✓ File exists: {file_name}")
    
    def setup_development_environment(self):
        """Set up development environment."""
        self.log("Setting up development environment...")
        
        # Create necessary directories
        dirs_to_create = [
            "uploads",
            "logs",
            "data",
            "temp"
        ]
        
        for dir_name in dirs_to_create:
            dir_path = self.project_root / dir_name
            dir_path.mkdir(exist_ok=True)
            self.log(f"Created directory: {dir_name}")
        
        # Create .gitignore if missing
        gitignore_path = self.project_root / ".gitignore"
        if not gitignore_path.exists():
            self.create_gitignore()
        
        self.fixes_applied.append("Development environment configured")
    
    def create_gitignore(self):
        """Create a comprehensive .gitignore file."""
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
logs/
*.log

# Database
*.db
*.sqlite
*.sqlite3

# Uploads
uploads/
temp/

# Environment
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Next.js
.next/
out/

# Coverage
.coverage
htmlcov/
.pytest_cache/

# Security
*.pem
*.key
*.crt

# Terraform
*.tfstate
*.tfstate.*
.terraform/

# Kubernetes
*.kubeconfig
"""
        
        with open(self.project_root / ".gitignore", "w") as f:
            f.write(gitignore_content)
    
    def run_health_checks(self):
        """Run health checks."""
        self.log("Running health checks...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 13):
            self.issues_found.append(f"Python version {python_version.major}.{python_version.minor} is below required 3.13")
        else:
            self.log(f"✓ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check Node.js version
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            node_version = result.stdout.strip()
            self.log(f"✓ Node.js version: {node_version}")
        except Exception as e:
            self.issues_found.append(f"Node.js not found: {e}")
        
        # Check if services can be imported
        self.check_service_imports()
    
    def check_service_imports(self):
        """Check if all services can be imported."""
        services_to_check = [
            "services.api_gateway.main",
            "services.auth_service.auth",
            "services.search_service.retrieval_agent",
            "services.synthesis_service.synthesis_agent",
            "services.factcheck_service.factcheck_agent",
            "services.analytics_service.analytics"
        ]
        
        for service in services_to_check:
            try:
                __import__(service)
                self.log(f"✓ Service import successful: {service}")
            except ImportError as e:
                self.issues_found.append(f"Service import failed: {service} - {e}")
    
    def generate_fix_report(self):
        """Generate a comprehensive fix report."""
        self.log("Generating fix report...")
        
        report = {
            "timestamp": str(Path(__file__).stat().st_mtime),
            "issues_found": self.issues_found,
            "fixes_applied": self.fixes_applied,
            "recommendations": self.generate_recommendations()
        }
        
        report_path = self.project_root / "setup_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        self.log(f"Fix report saved to: {report_path}")
        return report
    
    def generate_recommendations(self):
        """Generate recommendations for further improvements."""
        return [
            "Configure your .env file with actual API keys and database URLs",
            "Set up a proper database (PostgreSQL recommended for production)",
            "Configure Redis for caching and session management",
            "Set up monitoring with Prometheus and Grafana",
            "Implement proper logging with structured data",
            "Add comprehensive test coverage (aim for 90%+)",
            "Set up CI/CD pipeline with GitHub Actions",
            "Configure security scanning with Bandit and Safety",
            "Implement proper error handling and retry mechanisms",
            "Add rate limiting and DDoS protection",
            "Set up backup and disaster recovery procedures",
            "Configure SSL/TLS for production deployment",
            "Implement proper user authentication and authorization",
            "Add API documentation with OpenAPI/Swagger",
            "Set up performance monitoring and alerting"
        ]
    
    def run(self):
        """Run the comprehensive setup."""
        self.log("Starting comprehensive SarvanOM setup...")
        
        try:
            self.fix_missing_dependencies()
            self.setup_environment()
            self.fix_import_paths()
            self.validate_project_structure()
            self.setup_development_environment()
            self.run_health_checks()
            
            report = self.generate_fix_report()
            
            self.log("=" * 50)
            self.log("SETUP COMPLETE")
            self.log("=" * 50)
            
            if self.issues_found:
                self.log(f"⚠️  {len(self.issues_found)} issues found:")
                for issue in self.issues_found:
                    self.log(f"  - {issue}")
            
            if self.fixes_applied:
                self.log(f"✅ {len(self.fixes_applied)} fixes applied:")
                for fix in self.fixes_applied:
                    self.log(f"  - {fix}")
            
            if report["recommendations"]:
                self.log("📋 Recommendations for further improvements:")
                for rec in report["recommendations"]:
                    self.log(f"  - {rec}")
            
            self.log("=" * 50)
            self.log("Next steps:")
            self.log("1. Configure your .env file with actual values")
            self.log("2. Run: npm run dev")
            self.log("3. Access the application at http://localhost:3000")
            self.log("4. API documentation at http://localhost:8000/docs")
            
        except Exception as e:
            self.log(f"Setup failed: {e}", "ERROR")
            sys.exit(1)

if __name__ == "__main__":
    setup = SarvanOMSetup()
    setup.run() 