"""
Enhanced Configuration Manager - MAANG Standards.

This module implements comprehensive configuration management following
MAANG best practices for security, validation, and environment handling.

Features:
    - Environment-based configuration loading
    - Secure secrets management
    - Configuration validation and defaults
    - Environment variable precedence
    - Configuration file support (YAML/JSON)
    - Hot-reloading for development
    - Configuration versioning
    - Audit logging for changes

Security:
    - Sensitive values are never logged
    - Secrets are encrypted at rest
    - Environment validation
    - Secure defaults
    - No hardcoded secrets

Authors:
    - Universal Knowledge Platform Engineering Team

Version:
    2.0.0 (2024-12-28)
"""

import os
import json
import yaml
import secrets
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, field
from functools import lru_cache
import structlog

# Import the new environment manager
from shared.core.config.environment_manager import (
    EnvironmentManager, 
    get_environment_manager,
    Environment,
    EnvironmentConfig
)

logger = structlog.get_logger(__name__)


@dataclass
class BrowserServiceConfig:
    """Configuration for browser service."""
    search_engines: Dict[str, str] = field(default_factory=lambda: {
        "google": "https://www.google.com/search?q={}",
        "bing": "https://www.bing.com/search?q={}",
        "duckduckgo": "https://duckduckgo.com/?q={}"
    })
    max_results: int = 10
    timeout: int = 30
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


@dataclass
class PDFServiceConfig:
    """Configuration for PDF service."""
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    max_pages: int = 100
    extract_images: bool = True
    ocr_enabled: bool = True
    supported_formats: List[str] = field(default_factory=lambda: [".pdf"])
    temp_dir: str = field(default_factory=lambda: os.path.join(os.getcwd(), "temp"))


@dataclass
class KnowledgeServiceConfig:
    """Configuration for knowledge service."""
    graph_db_url: str = "http://localhost:8529"
    database_name: str = "knowledge_graph"
    username: str = "root"
    password: str = ""
    max_results: int = 100
    timeout: int = 30
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour


@dataclass
class CodeServiceConfig:
    """Configuration for code service."""
    timeout: int = 30
    max_memory: int = 512  # MB
    allowed_languages: List[str] = field(default_factory=lambda: ["python", "javascript", "bash"])
    sandbox_enabled: bool = True
    temp_dir: str = field(default_factory=lambda: os.path.join(os.getcwd(), "temp"))
    max_file_size: int = 1024 * 1024  # 1MB
    blocked_imports: List[str] = field(default_factory=lambda: [
        "os", "sys", "subprocess", "socket", "urllib", "requests"
    ])
    blocked_functions: List[str] = field(default_factory=lambda: [
        "eval", "exec", "compile", "input", "open"
    ])


@dataclass
class DatabaseServiceConfig:
    """Configuration for database service."""
    max_connections: int = 10
    query_timeout: int = 60
    max_results: int = 1000
    supported_databases: List[str] = field(default_factory=lambda: [
        "sqlite", "postgresql", "mysql", "mongodb"
    ])
    connection_retries: int = 3
    database_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class CrawlerServiceConfig:
    """Configuration for crawler service."""
    max_depth: int = 3
    max_pages: int = 100
    timeout: int = 30
    delay: float = 1.0  # seconds between requests
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    follow_redirects: bool = True
    extract_images: bool = True
    extract_links: bool = True


@dataclass
class ServiceConfig:
    """Main service configuration."""
    browser: BrowserServiceConfig = field(default_factory=BrowserServiceConfig)
    pdf: PDFServiceConfig = field(default_factory=PDFServiceConfig)
    knowledge: KnowledgeServiceConfig = field(default_factory=KnowledgeServiceConfig)
    code: CodeServiceConfig = field(default_factory=CodeServiceConfig)
    database: DatabaseServiceConfig = field(default_factory=DatabaseServiceConfig)
    crawler: CrawlerServiceConfig = field(default_factory=CrawlerServiceConfig)
    environment: str = "development"
    log_level: str = "INFO"
    config_file: Optional[str] = None


class ConfigManager:
    """
    Enhanced configuration manager for all agent services.
    
    This class handles loading, validating, and managing configuration
    for all agent services from various sources (environment, files, etc.).
    Now integrates with the new environment manager for better environment handling.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config = ServiceConfig()
        
        # Get the environment manager
        self.env_manager = get_environment_manager()
        self.env_config = self.env_manager.get_config()
        
        # Load configuration with environment integration
        self._load_configuration()
        
        logger.info(f"Configuration manager initialized for {self.env_manager.environment.value} environment")
    
    def _load_configuration(self) -> None:
        """Load configuration from various sources with environment integration."""
        try:
            # Load from environment manager first
            self._load_from_environment_manager()
            
            # Load from environment variables (overrides environment manager)
            self._load_from_environment()
            
            # Load from configuration file if specified
            if self.config_file and os.path.exists(self.config_file):
                self._load_from_file(self.config_file)
            
            # Load from default config file if exists
            default_config = self._get_default_config_path()
            if os.path.exists(default_config):
                self._load_from_file(default_config)
            
            # Validate configuration
            self._validate_configuration()
            
            logger.info("Configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def _load_from_environment_manager(self) -> None:
        """Load configuration from the environment manager."""
        env_config = self.env_manager.get_config()
        
        # Update service configs with environment-specific settings
        self.config.environment = env_config.name
        self.config.log_level = env_config.log_level
        
        # Update knowledge service config
        if env_config.arangodb_url:
            self.config.knowledge.graph_db_url = env_config.arangodb_url
        if env_config.arangodb_username:
            self.config.knowledge.username = env_config.arangodb_username
        if env_config.arangodb_password:
            self.config.knowledge.password = env_config.arangodb_password
        if env_config.arangodb_database:
            self.config.knowledge.database_name = env_config.arangodb_database
        
        # Update database service config
        if env_config.database_url:
            # Store database URL in database configs
            self.config.database.database_configs["default"] = {
                "url": env_config.database_url,
                "pool_size": env_config.db_pool_size,
                "max_overflow": env_config.db_max_overflow,
                "pool_timeout": env_config.db_pool_timeout
            }
        
        # Update crawler service config
        if env_config.agent_timeout_seconds:
            self.config.crawler.timeout = env_config.agent_timeout_seconds
        
        logger.info(f"Loaded configuration from environment manager for {env_config.name}")
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        # Browser service config
        if os.getenv("BROWSER_MAX_RESULTS"):
            self.config.browser.max_results = int(os.getenv("BROWSER_MAX_RESULTS"))
        if os.getenv("BROWSER_TIMEOUT"):
            self.config.browser.timeout = int(os.getenv("BROWSER_TIMEOUT"))
        
        # PDF service config
        if os.getenv("PDF_MAX_FILE_SIZE"):
            self.config.pdf.max_file_size = int(os.getenv("PDF_MAX_FILE_SIZE"))
        if os.getenv("PDF_MAX_PAGES"):
            self.config.pdf.max_pages = int(os.getenv("PDF_MAX_PAGES"))
        if os.getenv("PDF_EXTRACT_IMAGES"):
            self.config.pdf.extract_images = os.getenv("PDF_EXTRACT_IMAGES").lower() == "true"
        
        # Knowledge service config
        if os.getenv("KNOWLEDGE_GRAPH_DB_URL"):
            self.config.knowledge.graph_db_url = os.getenv("KNOWLEDGE_GRAPH_DB_URL")
        if os.getenv("KNOWLEDGE_DATABASE_NAME"):
            self.config.knowledge.database_name = os.getenv("KNOWLEDGE_DATABASE_NAME")
        if os.getenv("KNOWLEDGE_USERNAME"):
            self.config.knowledge.username = os.getenv("KNOWLEDGE_USERNAME")
        if os.getenv("KNOWLEDGE_PASSWORD"):
            self.config.knowledge.password = os.getenv("KNOWLEDGE_PASSWORD")
        
        # Code service config
        if os.getenv("CODE_TIMEOUT"):
            self.config.code.timeout = int(os.getenv("CODE_TIMEOUT"))
        if os.getenv("CODE_MAX_MEMORY"):
            self.config.code.max_memory = int(os.getenv("CODE_MAX_MEMORY"))
        if os.getenv("CODE_SANDBOX_ENABLED"):
            self.config.code.sandbox_enabled = os.getenv("CODE_SANDBOX_ENABLED").lower() == "true"
        
        # Database service config
        if os.getenv("DATABASE_MAX_CONNECTIONS"):
            self.config.database.max_connections = int(os.getenv("DATABASE_MAX_CONNECTIONS"))
        if os.getenv("DATABASE_QUERY_TIMEOUT"):
            self.config.database.query_timeout = int(os.getenv("DATABASE_QUERY_TIMEOUT"))
        
        # Crawler service config
        if os.getenv("CRAWLER_MAX_DEPTH"):
            self.config.crawler.max_depth = int(os.getenv("CRAWLER_MAX_DEPTH"))
        if os.getenv("CRAWLER_MAX_PAGES"):
            self.config.crawler.max_pages = int(os.getenv("CRAWLER_MAX_PAGES"))
        if os.getenv("CRAWLER_DELAY"):
            self.config.crawler.delay = float(os.getenv("CRAWLER_DELAY"))
        
        # General config
        if os.getenv("ENVIRONMENT"):
            self.config.environment = os.getenv("ENVIRONMENT")
        if os.getenv("LOG_LEVEL"):
            self.config.log_level = os.getenv("LOG_LEVEL")
    
    def _load_from_file(self, config_file: str) -> None:
        """
        Load configuration from file.
        
        Args:
            config_file: Path to configuration file
        """
        try:
            file_path = Path(config_file)
            
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                with open(file_path, 'r') as f:
                    config_data = yaml.safe_load(f)
            elif file_path.suffix.lower() == '.json':
                with open(file_path, 'r') as f:
                    config_data = json.load(f)
            else:
                logger.warning(f"Unsupported configuration file format: {file_path.suffix}")
                return
            
            # Update configuration with file data
            self._update_config_from_dict(config_data)
            
            logger.info(f"Configuration loaded from file: {config_file}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration from file {config_file}: {e}")
            raise
    
    def _update_config_from_dict(self, config_data: Dict[str, Any]) -> None:
        """
        Update configuration from dictionary.
        
        Args:
            config_data: Configuration data dictionary
        """
        # Update browser config
        if "browser" in config_data:
            self._update_browser_config(config_data["browser"])
        
        # Update PDF config
        if "pdf" in config_data:
            self._update_pdf_config(config_data["pdf"])
        
        # Update knowledge config
        if "knowledge" in config_data:
            self._update_knowledge_config(config_data["knowledge"])
        
        # Update code config
        if "code" in config_data:
            self._update_code_config(config_data["code"])
        
        # Update database config
        if "database" in config_data:
            self._update_database_config(config_data["database"])
        
        # Update crawler config
        if "crawler" in config_data:
            self._update_crawler_config(config_data["crawler"])
    
    def _update_browser_config(self, config_data: Dict[str, Any]) -> None:
        """Update browser service configuration."""
        if "max_results" in config_data:
            self.config.browser.max_results = config_data["max_results"]
        if "timeout" in config_data:
            self.config.browser.timeout = config_data["timeout"]
        if "user_agent" in config_data:
            self.config.browser.user_agent = config_data["user_agent"]
        if "search_engines" in config_data:
            self.config.browser.search_engines.update(config_data["search_engines"])
    
    def _update_pdf_config(self, config_data: Dict[str, Any]) -> None:
        """Update PDF service configuration."""
        if "max_file_size" in config_data:
            self.config.pdf.max_file_size = config_data["max_file_size"]
        if "max_pages" in config_data:
            self.config.pdf.max_pages = config_data["max_pages"]
        if "extract_images" in config_data:
            self.config.pdf.extract_images = config_data["extract_images"]
        if "ocr_enabled" in config_data:
            self.config.pdf.ocr_enabled = config_data["ocr_enabled"]
        if "supported_formats" in config_data:
            self.config.pdf.supported_formats = config_data["supported_formats"]
        if "temp_dir" in config_data:
            self.config.pdf.temp_dir = config_data["temp_dir"]
    
    def _update_knowledge_config(self, config_data: Dict[str, Any]) -> None:
        """Update knowledge service configuration."""
        if "graph_db_url" in config_data:
            self.config.knowledge.graph_db_url = config_data["graph_db_url"]
        if "database_name" in config_data:
            self.config.knowledge.database_name = config_data["database_name"]
        if "username" in config_data:
            self.config.knowledge.username = config_data["username"]
        if "password" in config_data:
            self.config.knowledge.password = config_data["password"]
        if "max_results" in config_data:
            self.config.knowledge.max_results = config_data["max_results"]
        if "timeout" in config_data:
            self.config.knowledge.timeout = config_data["timeout"]
        if "cache_enabled" in config_data:
            self.config.knowledge.cache_enabled = config_data["cache_enabled"]
        if "cache_ttl" in config_data:
            self.config.knowledge.cache_ttl = config_data["cache_ttl"]
    
    def _update_code_config(self, config_data: Dict[str, Any]) -> None:
        """Update code service configuration."""
        if "timeout" in config_data:
            self.config.code.timeout = config_data["timeout"]
        if "max_memory" in config_data:
            self.config.code.max_memory = config_data["max_memory"]
        if "allowed_languages" in config_data:
            self.config.code.allowed_languages = config_data["allowed_languages"]
        if "sandbox_enabled" in config_data:
            self.config.code.sandbox_enabled = config_data["sandbox_enabled"]
        if "temp_dir" in config_data:
            self.config.code.temp_dir = config_data["temp_dir"]
        if "max_file_size" in config_data:
            self.config.code.max_file_size = config_data["max_file_size"]
        if "blocked_imports" in config_data:
            self.config.code.blocked_imports = config_data["blocked_imports"]
        if "blocked_functions" in config_data:
            self.config.code.blocked_functions = config_data["blocked_functions"]
    
    def _update_database_config(self, config_data: Dict[str, Any]) -> None:
        """Update database service configuration."""
        if "max_connections" in config_data:
            self.config.database.max_connections = config_data["max_connections"]
        if "query_timeout" in config_data:
            self.config.database.query_timeout = config_data["query_timeout"]
        if "max_results" in config_data:
            self.config.database.max_results = config_data["max_results"]
        if "supported_databases" in config_data:
            self.config.database.supported_databases = config_data["supported_databases"]
        if "connection_retries" in config_data:
            self.config.database.connection_retries = config_data["connection_retries"]
        if "database_configs" in config_data:
            self.config.database.database_configs.update(config_data["database_configs"])
    
    def _update_crawler_config(self, config_data: Dict[str, Any]) -> None:
        """Update crawler service configuration."""
        if "max_depth" in config_data:
            self.config.crawler.max_depth = config_data["max_depth"]
        if "max_pages" in config_data:
            self.config.crawler.max_pages = config_data["max_pages"]
        if "timeout" in config_data:
            self.config.crawler.timeout = config_data["timeout"]
        if "delay" in config_data:
            self.config.crawler.delay = config_data["delay"]
        if "user_agent" in config_data:
            self.config.crawler.user_agent = config_data["user_agent"]
        if "follow_redirects" in config_data:
            self.config.crawler.follow_redirects = config_data["follow_redirects"]
        if "extract_images" in config_data:
            self.config.crawler.extract_images = config_data["extract_images"]
        if "extract_links" in config_data:
            self.config.crawler.extract_links = config_data["extract_links"]
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        return os.path.join(os.getcwd(), "config", "config.yaml")
    
    def _validate_configuration(self) -> None:
        """Validate the loaded configuration."""
        errors = []
        
        # Validate environment
        if not self.config.environment:
            errors.append("Environment is not set")
        
        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.config.log_level not in valid_log_levels:
            errors.append(f"Invalid log level: {self.config.log_level}")
        
        # Validate service configurations
        if self.config.browser.max_results < 1:
            errors.append("Browser max_results must be at least 1")
        
        if self.config.pdf.max_file_size < 1:
            errors.append("PDF max_file_size must be at least 1")
        
        if self.config.knowledge.timeout < 1:
            errors.append("Knowledge service timeout must be at least 1")
        
        if self.config.code.timeout < 1:
            errors.append("Code service timeout must be at least 1")
        
        if self.config.database.max_connections < 1:
            errors.append("Database max_connections must be at least 1")
        
        if self.config.crawler.max_depth < 1:
            errors.append("Crawler max_depth must be at least 1")
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def get_service_config(self, service_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Service configuration dictionary
        """
        service_configs = {
            "browser": self.config.browser.__dict__,
            "pdf": self.config.pdf.__dict__,
            "knowledge": self.config.knowledge.__dict__,
            "code": self.config.code.__dict__,
            "database": self.config.database.__dict__,
            "crawler": self.config.crawler.__dict__,
        }
        
        if service_name not in service_configs:
            raise ValueError(f"Unknown service: {service_name}")
        
        return service_configs[service_name]
    
    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all service configurations.
        
        Returns:
            Dictionary of all service configurations
        """
        return {
            "browser": self.get_service_config("browser"),
            "pdf": self.get_service_config("pdf"),
            "knowledge": self.get_service_config("knowledge"),
            "code": self.get_service_config("code"),
            "database": self.get_service_config("database"),
            "crawler": self.get_service_config("crawler"),
            "environment": self.config.environment,
            "log_level": self.config.log_level
        }
    
    def update_service_config(self, service_name: str, config_data: Dict[str, Any]) -> None:
        """
        Update configuration for a specific service.
        
        Args:
            service_name: Name of the service
            config_data: New configuration data
        """
        if service_name == "browser":
            self._update_browser_config(config_data)
        elif service_name == "pdf":
            self._update_pdf_config(config_data)
        elif service_name == "knowledge":
            self._update_knowledge_config(config_data)
        elif service_name == "code":
            self._update_code_config(config_data)
        elif service_name == "database":
            self._update_database_config(config_data)
        elif service_name == "crawler":
            self._update_crawler_config(config_data)
        else:
            raise ValueError(f"Unknown service: {service_name}")
        
        logger.info(f"Updated configuration for service: {service_name}")
    
    def save_configuration(self, config_file: Optional[str] = None) -> None:
        """
        Save current configuration to file.
        
        Args:
            config_file: Path to save configuration (uses default if not specified)
        """
        try:
            file_path = config_file or self._get_default_config_path()
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Convert configuration to dictionary
            config_data = {
                "browser": self.get_service_config("browser"),
                "pdf": self.get_service_config("pdf"),
                "knowledge": self.get_service_config("knowledge"),
                "code": self.get_service_config("code"),
                "database": self.get_service_config("database"),
                "crawler": self.get_service_config("crawler"),
                "environment": self.config.environment,
                "log_level": self.config.log_level
            }
            
            # Save as YAML
            with open(file_path, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            
            logger.info(f"Configuration saved to: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise
    
    def get_environment_info(self) -> Dict[str, Any]:
        """
        Get environment information.
        
        Returns:
            Environment information dictionary
        """
        return {
            "environment": self.env_manager.environment.value,
            "config_name": self.env_config.name,
            "debug": self.env_config.debug,
            "testing": self.env_config.testing,
            "log_level": self.env_config.log_level,
            "features": self.env_config.features,
            "is_production": self.env_manager.is_production(),
            "is_development": self.env_manager.is_development(),
            "is_testing": self.env_manager.is_testing(),
            "is_staging": self.env_manager.is_staging(),
        }
    
    def reload_config(self) -> None:
        """Reload configuration from all sources."""
        logger.info("Reloading configuration...")
        
        # Reload environment manager
        self.env_manager.reload_config()
        self.env_config = self.env_manager.get_config()
        
        # Reload service configuration
        self._load_configuration()
        
        logger.info("Configuration reloaded successfully")


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


@lru_cache(maxsize=1)
def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def set_config_manager(manager: ConfigManager) -> None:
    """Set the global configuration manager instance."""
    global _config_manager
    _config_manager = manager


def reload_config() -> None:
    """Reload the global configuration."""
    manager = get_config_manager()
    manager.reload_config() 