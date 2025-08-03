"""
Service Configuration Management

This module provides configuration management for all agent services.
It handles environment-based configuration, service-specific settings,
and configuration validation.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import yaml
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


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
    Configuration manager for all agent services.
    
    This class handles loading, validating, and managing configuration
    for all agent services from various sources (environment, files, etc.).
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config = ServiceConfig()
        self._load_configuration()
        logger.info("Configuration manager initialized")
    
    def _load_configuration(self) -> None:
        """Load configuration from various sources."""
        try:
            # Load from environment variables first
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
            browser_config = config_data["browser"]
            if "search_engines" in browser_config:
                self.config.browser.search_engines.update(browser_config["search_engines"])
            if "max_results" in browser_config:
                self.config.browser.max_results = browser_config["max_results"]
            if "timeout" in browser_config:
                self.config.browser.timeout = browser_config["timeout"]
        
        # Update PDF config
        if "pdf" in config_data:
            pdf_config = config_data["pdf"]
            if "max_file_size" in pdf_config:
                self.config.pdf.max_file_size = pdf_config["max_file_size"]
            if "max_pages" in pdf_config:
                self.config.pdf.max_pages = pdf_config["max_pages"]
            if "extract_images" in pdf_config:
                self.config.pdf.extract_images = pdf_config["extract_images"]
        
        # Update knowledge config
        if "knowledge" in config_data:
            knowledge_config = config_data["knowledge"]
            if "graph_db_url" in knowledge_config:
                self.config.knowledge.graph_db_url = knowledge_config["graph_db_url"]
            if "database_name" in knowledge_config:
                self.config.knowledge.database_name = knowledge_config["database_name"]
            if "username" in knowledge_config:
                self.config.knowledge.username = knowledge_config["username"]
            if "password" in knowledge_config:
                self.config.knowledge.password = knowledge_config["password"]
        
        # Update code config
        if "code" in config_data:
            code_config = config_data["code"]
            if "timeout" in code_config:
                self.config.code.timeout = code_config["timeout"]
            if "max_memory" in code_config:
                self.config.code.max_memory = code_config["max_memory"]
            if "allowed_languages" in code_config:
                self.config.code.allowed_languages = code_config["allowed_languages"]
            if "sandbox_enabled" in code_config:
                self.config.code.sandbox_enabled = code_config["sandbox_enabled"]
        
        # Update database config
        if "database" in config_data:
            database_config = config_data["database"]
            if "max_connections" in database_config:
                self.config.database.max_connections = database_config["max_connections"]
            if "query_timeout" in database_config:
                self.config.database.query_timeout = database_config["query_timeout"]
            if "database_configs" in database_config:
                self.config.database.database_configs.update(database_config["database_configs"])
        
        # Update crawler config
        if "crawler" in config_data:
            crawler_config = config_data["crawler"]
            if "max_depth" in crawler_config:
                self.config.crawler.max_depth = crawler_config["max_depth"]
            if "max_pages" in crawler_config:
                self.config.crawler.max_pages = crawler_config["max_pages"]
            if "delay" in crawler_config:
                self.config.crawler.delay = crawler_config["delay"]
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path."""
        return os.path.join(os.getcwd(), "config", "services.yaml")
    
    def _validate_configuration(self) -> None:
        """Validate configuration values."""
        try:
            # Validate browser config
            if self.config.browser.max_results <= 0:
                raise ValueError("Browser max_results must be positive")
            if self.config.browser.timeout <= 0:
                raise ValueError("Browser timeout must be positive")
            
            # Validate PDF config
            if self.config.pdf.max_file_size <= 0:
                raise ValueError("PDF max_file_size must be positive")
            if self.config.pdf.max_pages <= 0:
                raise ValueError("PDF max_pages must be positive")
            
            # Validate knowledge config
            if not self.config.knowledge.graph_db_url:
                raise ValueError("Knowledge graph_db_url cannot be empty")
            if not self.config.knowledge.database_name:
                raise ValueError("Knowledge database_name cannot be empty")
            
            # Validate code config
            if self.config.code.timeout <= 0:
                raise ValueError("Code timeout must be positive")
            if self.config.code.max_memory <= 0:
                raise ValueError("Code max_memory must be positive")
            if not self.config.code.allowed_languages:
                raise ValueError("Code allowed_languages cannot be empty")
            
            # Validate database config
            if self.config.database.max_connections <= 0:
                raise ValueError("Database max_connections must be positive")
            if self.config.database.query_timeout <= 0:
                raise ValueError("Database query_timeout must be positive")
            
            # Validate crawler config
            if self.config.crawler.max_depth <= 0:
                raise ValueError("Crawler max_depth must be positive")
            if self.config.crawler.max_pages <= 0:
                raise ValueError("Crawler max_pages must be positive")
            if self.config.crawler.delay < 0:
                raise ValueError("Crawler delay must be non-negative")
            
            logger.info("Configuration validation passed")
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            raise
    
    def get_service_config(self, service_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Service configuration dictionary
        """
        config_map = {
            "browser": self.config.browser,
            "pdf": self.config.pdf,
            "knowledge": self.config.knowledge,
            "code": self.config.code,
            "database": self.config.database,
            "crawler": self.config.crawler
        }
        
        if service_name not in config_map:
            raise ValueError(f"Unknown service: {service_name}")
        
        # Convert dataclass to dictionary
        config = config_map[service_name]
        return {k: v for k, v in config.__dict__.items()}
    
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
            "crawler": self.get_service_config("crawler")
        }
    
    def update_service_config(self, service_name: str, config_data: Dict[str, Any]) -> None:
        """
        Update configuration for a specific service.
        
        Args:
            service_name: Name of the service
            config_data: New configuration data
        """
        try:
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
            
            # Re-validate configuration
            self._validate_configuration()
            
            logger.info(f"Updated configuration for {service_name} service")
            
        except Exception as e:
            logger.error(f"Failed to update configuration for {service_name}: {e}")
            raise
    
    def _update_browser_config(self, config_data: Dict[str, Any]) -> None:
        """Update browser service configuration."""
        if "search_engines" in config_data:
            self.config.browser.search_engines.update(config_data["search_engines"])
        if "max_results" in config_data:
            self.config.browser.max_results = config_data["max_results"]
        if "timeout" in config_data:
            self.config.browser.timeout = config_data["timeout"]
    
    def _update_pdf_config(self, config_data: Dict[str, Any]) -> None:
        """Update PDF service configuration."""
        if "max_file_size" in config_data:
            self.config.pdf.max_file_size = config_data["max_file_size"]
        if "max_pages" in config_data:
            self.config.pdf.max_pages = config_data["max_pages"]
        if "extract_images" in config_data:
            self.config.pdf.extract_images = config_data["extract_images"]
    
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
    
    def _update_database_config(self, config_data: Dict[str, Any]) -> None:
        """Update database service configuration."""
        if "max_connections" in config_data:
            self.config.database.max_connections = config_data["max_connections"]
        if "query_timeout" in config_data:
            self.config.database.query_timeout = config_data["query_timeout"]
        if "database_configs" in config_data:
            self.config.database.database_configs.update(config_data["database_configs"])
    
    def _update_crawler_config(self, config_data: Dict[str, Any]) -> None:
        """Update crawler service configuration."""
        if "max_depth" in config_data:
            self.config.crawler.max_depth = config_data["max_depth"]
        if "max_pages" in config_data:
            self.config.crawler.max_pages = config_data["max_pages"]
        if "delay" in config_data:
            self.config.crawler.delay = config_data["delay"]
    
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


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """
    Get the global configuration manager instance.
    
    Returns:
        The global configuration manager
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def set_config_manager(manager: ConfigManager) -> None:
    """
    Set the global configuration manager instance.
    
    Args:
        manager: The configuration manager to set as global
    """
    global _config_manager
    _config_manager = manager 