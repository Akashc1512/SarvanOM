"""
Advanced Logging Configuration Manager

This module provides enterprise-grade configuration management for the unified logging system.
It extends the basic unified logging with advanced configuration features, validation,
and hot-reloading capabilities for production environments.

Features:
- Configuration validation and schema checking
- Hot-reload configuration without service restart
- Environment-specific configuration profiles
- Configuration versioning and rollback
- Integration with external configuration systems
- Audit logging for configuration changes

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2024-12-28)
"""

import os
import json
import yaml
import time
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from enum import Enum
import threading
import hashlib

from .unified_logging import get_logger, setup_logging
from .production_logging import setup_production_logging


class LogLevel(str, Enum):
    """Valid log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(str, Enum):
    """Valid log formats."""
    TEXT = "text"
    JSON = "json"


class Environment(str, Enum):
    """Valid environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class LoggingConfigProfile:
    """Configuration profile for logging settings."""
    
    # Basic settings
    service_name: str = "sarvanom"
    version: str = "1.0.0"
    environment: Environment = Environment.DEVELOPMENT
    
    # Logging levels
    log_level: LogLevel = LogLevel.INFO
    log_format: LogFormat = LogFormat.TEXT
    
    # File configuration
    log_file: Optional[str] = None
    max_file_size_mb: int = 100
    backup_count: int = 5
    
    # Performance settings
    buffer_size: int = 10000
    flush_interval: int = 5
    
    # Security settings
    mask_sensitive_data: bool = True
    log_user_data: bool = False
    audit_enabled: bool = True
    
    # Production features
    enable_metrics: bool = False
    enable_health_logging: bool = False
    enable_security_logging: bool = False
    enable_performance_monitoring: bool = False
    
    # Alert thresholds
    error_rate_threshold: float = 5.0
    response_time_threshold: float = 5000.0
    cache_hit_rate_threshold: float = 70.0
    
    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    config_version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LoggingConfigProfile':
        """Create from dictionary."""
        # Handle enum conversions
        if 'environment' in data and isinstance(data['environment'], str):
            data['environment'] = Environment(data['environment'])
        if 'log_level' in data and isinstance(data['log_level'], str):
            data['log_level'] = LogLevel(data['log_level'])
        if 'log_format' in data and isinstance(data['log_format'], str):
            data['log_format'] = LogFormat(data['log_format'])
        
        # Handle datetime conversions
        for field_name in ['created_at', 'updated_at']:
            if field_name in data and isinstance(data[field_name], str):
                data[field_name] = datetime.fromisoformat(data[field_name])
        
        return cls(**data)


class ConfigurationValidator:
    """Validates logging configuration profiles."""
    
    @staticmethod
    def validate_profile(profile: LoggingConfigProfile) -> List[str]:
        """Validate configuration profile and return list of errors."""
        errors = []
        
        # Validate service name
        if not profile.service_name or not profile.service_name.strip():
            errors.append("Service name cannot be empty")
        
        # Validate file path if specified
        if profile.log_file:
            log_path = Path(profile.log_file)
            try:
                log_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create log directory: {e}")
        
        # Validate file size and backup count
        if profile.max_file_size_mb <= 0:
            errors.append("Max file size must be positive")
        
        if profile.backup_count < 0:
            errors.append("Backup count cannot be negative")
        
        # Validate buffer settings
        if profile.buffer_size <= 0:
            errors.append("Buffer size must be positive")
        
        if profile.flush_interval <= 0:
            errors.append("Flush interval must be positive")
        
        # Validate thresholds
        if profile.error_rate_threshold < 0 or profile.error_rate_threshold > 100:
            errors.append("Error rate threshold must be between 0 and 100")
        
        if profile.response_time_threshold <= 0:
            errors.append("Response time threshold must be positive")
        
        if profile.cache_hit_rate_threshold < 0 or profile.cache_hit_rate_threshold > 100:
            errors.append("Cache hit rate threshold must be between 0 and 100")
        
        return errors
    
    @staticmethod
    def validate_environment_consistency(profile: LoggingConfigProfile) -> List[str]:
        """Validate that settings are appropriate for the environment."""
        warnings = []
        
        if profile.environment == Environment.PRODUCTION:
            if profile.log_level == LogLevel.DEBUG:
                warnings.append("DEBUG level not recommended for production")
            
            if profile.log_format == LogFormat.TEXT:
                warnings.append("JSON format recommended for production monitoring")
            
            if not profile.log_file:
                warnings.append("File logging recommended for production")
            
            if not profile.enable_metrics:
                warnings.append("Metrics collection recommended for production")
        
        elif profile.environment == Environment.DEVELOPMENT:
            if profile.log_format == LogFormat.JSON and profile.log_level != LogLevel.DEBUG:
                warnings.append("TEXT format may be more readable for development")
        
        return warnings


class LoggingConfigurationManager:
    """
    Advanced configuration manager for logging system.
    
    Provides configuration loading, validation, hot-reload capabilities,
    and integration with external configuration systems.
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path("config/logging")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_profile: Optional[LoggingConfigProfile] = None
        self.profile_history: List[LoggingConfigProfile] = []
        self.validator = ConfigurationValidator()
        self.lock = threading.Lock()
        
        # Set up monitoring for config file changes
        self._config_file_hashes: Dict[str, str] = {}
        self._monitor_thread: Optional[threading.Thread] = None
        self._monitoring_enabled = False
        
        self.logger = get_logger(__name__)
    
    def create_default_profiles(self):
        """Create default configuration profiles for each environment."""
        profiles = {
            Environment.DEVELOPMENT: LoggingConfigProfile(
                environment=Environment.DEVELOPMENT,
                log_level=LogLevel.DEBUG,
                log_format=LogFormat.TEXT,
                enable_metrics=False,
                enable_health_logging=False,
                enable_security_logging=False
            ),
            Environment.TESTING: LoggingConfigProfile(
                environment=Environment.TESTING,
                log_level=LogLevel.WARNING,
                log_format=LogFormat.JSON,
                enable_metrics=True,
                enable_health_logging=True,
                enable_security_logging=False
            ),
            Environment.STAGING: LoggingConfigProfile(
                environment=Environment.STAGING,
                log_level=LogLevel.INFO,
                log_format=LogFormat.JSON,
                log_file="/var/log/sarvanom/staging.log",
                enable_metrics=True,
                enable_health_logging=True,
                enable_security_logging=True,
                enable_performance_monitoring=True
            ),
            Environment.PRODUCTION: LoggingConfigProfile(
                environment=Environment.PRODUCTION,
                log_level=LogLevel.INFO,
                log_format=LogFormat.JSON,
                log_file="/var/log/sarvanom/production.log",
                enable_metrics=True,
                enable_health_logging=True,
                enable_security_logging=True,
                enable_performance_monitoring=True,
                audit_enabled=True
            )
        }
        
        for env, profile in profiles.items():
            self.save_profile(profile, f"{env.value}.yaml")
        
        self.logger.info("Created default configuration profiles",
                        profiles_created=list(profiles.keys()),
                        component="config_manager")
    
    def load_profile(self, filename: str) -> LoggingConfigProfile:
        """Load configuration profile from file."""
        config_path = self.config_dir / filename
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r') as f:
                if filename.endswith('.yaml') or filename.endswith('.yml'):
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            profile = LoggingConfigProfile.from_dict(data)
            
            # Validate profile
            errors = self.validator.validate_profile(profile)
            if errors:
                raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
            
            # Log warnings
            warnings = self.validator.validate_environment_consistency(profile)
            if warnings:
                self.logger.warning("Configuration warnings",
                                  warnings=warnings,
                                  config_file=filename,
                                  component="config_manager")
            
            return profile
            
        except Exception as e:
            self.logger.error("Failed to load configuration profile",
                            config_file=filename,
                            error=str(e),
                            component="config_manager")
            raise
    
    def save_profile(self, profile: LoggingConfigProfile, filename: str):
        """Save configuration profile to file."""
        config_path = self.config_dir / filename
        
        # Validate before saving
        errors = self.validator.validate_profile(profile)
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        # Update timestamp
        profile.updated_at = datetime.now(timezone.utc)
        
        try:
            with open(config_path, 'w') as f:
                if filename.endswith('.yaml') or filename.endswith('.yml'):
                    yaml.dump(profile.to_dict(), f, default_flow_style=False)
                else:
                    json.dump(profile.to_dict(), f, indent=2, default=str)
            
            # Update file hash for monitoring
            self._update_file_hash(str(config_path))
            
            self.logger.info("Configuration profile saved",
                           config_file=filename,
                           profile_version=profile.config_version,
                           component="config_manager")
            
        except Exception as e:
            self.logger.error("Failed to save configuration profile",
                            config_file=filename,
                            error=str(e),
                            component="config_manager")
            raise
    
    def apply_profile(self, profile: LoggingConfigProfile):
        """Apply configuration profile to the logging system."""
        with self.lock:
            # Store current profile for history
            if self.current_profile:
                self.profile_history.append(self.current_profile)
            
            # Apply new configuration
            if profile.environment == Environment.PRODUCTION and profile.enable_metrics:
                setup_production_logging(
                    service_name=profile.service_name,
                    enable_collection=True
                )
            else:
                setup_logging(
                    service_name=profile.service_name,
                    version=profile.version,
                    log_level=profile.log_level.value,
                    log_format=profile.log_format.value,
                    log_file=profile.log_file
                )
            
            self.current_profile = profile
            
            self.logger.info("Configuration profile applied",
                           service_name=profile.service_name,
                           environment=profile.environment.value,
                           log_level=profile.log_level.value,
                           log_format=profile.log_format.value,
                           component="config_manager")
    
    def load_and_apply_environment_config(self, environment: Environment):
        """Load and apply configuration for specific environment."""
        config_file = f"{environment.value}.yaml"
        
        try:
            profile = self.load_profile(config_file)
            self.apply_profile(profile)
        except FileNotFoundError:
            self.logger.warning("Environment config not found, creating default",
                              environment=environment.value,
                              config_file=config_file,
                              component="config_manager")
            self.create_default_profiles()
            profile = self.load_profile(config_file)
            self.apply_profile(profile)
    
    def rollback_configuration(self) -> bool:
        """Rollback to previous configuration."""
        with self.lock:
            if not self.profile_history:
                self.logger.warning("No previous configuration to rollback to",
                                  component="config_manager")
                return False
            
            previous_profile = self.profile_history.pop()
            self.apply_profile(previous_profile)
            
            self.logger.info("Configuration rolled back",
                           profile_version=previous_profile.config_version,
                           component="config_manager")
            return True
    
    def start_monitoring(self, check_interval: int = 30):
        """Start monitoring configuration files for changes."""
        if self._monitoring_enabled:
            return
        
        self._monitoring_enabled = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_config_files,
            args=(check_interval,),
            daemon=True
        )
        self._monitor_thread.start()
        
        self.logger.info("Configuration monitoring started",
                        check_interval=check_interval,
                        component="config_manager")
    
    def stop_monitoring(self):
        """Stop monitoring configuration files."""
        self._monitoring_enabled = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        
        self.logger.info("Configuration monitoring stopped",
                        component="config_manager")
    
    def _monitor_config_files(self, check_interval: int):
        """Monitor configuration files for changes and reload if necessary."""
        while self._monitoring_enabled:
            try:
                for config_file in self.config_dir.glob("*.yaml"):
                    if self._has_file_changed(str(config_file)):
                        self.logger.info("Configuration file changed, reloading",
                                       config_file=config_file.name,
                                       component="config_manager")
                        
                        try:
                            profile = self.load_profile(config_file.name)
                            if self.current_profile and profile.environment == self.current_profile.environment:
                                self.apply_profile(profile)
                        except Exception as e:
                            self.logger.error("Failed to reload changed configuration",
                                            config_file=config_file.name,
                                            error=str(e),
                                            component="config_manager")
                
                time.sleep(check_interval)
                
            except Exception as e:
                self.logger.error("Error in configuration monitoring",
                                error=str(e),
                                component="config_manager")
                time.sleep(check_interval)
    
    def _update_file_hash(self, filepath: str):
        """Update stored hash for file."""
        try:
            with open(filepath, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            self._config_file_hashes[filepath] = file_hash
        except Exception:
            pass
    
    def _has_file_changed(self, filepath: str) -> bool:
        """Check if file has changed since last check."""
        try:
            with open(filepath, 'rb') as f:
                current_hash = hashlib.md5(f.read()).hexdigest()
            
            if filepath not in self._config_file_hashes:
                self._config_file_hashes[filepath] = current_hash
                return False
            
            if current_hash != self._config_file_hashes[filepath]:
                self._config_file_hashes[filepath] = current_hash
                return True
            
            return False
            
        except Exception:
            return False
    
    def get_current_configuration(self) -> Optional[LoggingConfigProfile]:
        """Get currently applied configuration."""
        return self.current_profile
    
    def list_available_profiles(self) -> List[str]:
        """List available configuration profiles."""
        profiles = []
        for config_file in self.config_dir.glob("*.yaml"):
            profiles.append(config_file.name)
        for config_file in self.config_dir.glob("*.json"):
            profiles.append(config_file.name)
        return sorted(profiles)


# Global configuration manager instance
_config_manager: Optional[LoggingConfigurationManager] = None


def get_configuration_manager() -> LoggingConfigurationManager:
    """Get global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = LoggingConfigurationManager()
    return _config_manager


def initialize_logging_for_environment(environment: str, 
                                     service_name: str = "sarvanom",
                                     enable_monitoring: bool = True):
    """
    Initialize logging system for specific environment.
    
    Args:
        environment: Environment name (development, testing, staging, production)
        service_name: Name of the service
        enable_monitoring: Whether to enable configuration monitoring
    """
    manager = get_configuration_manager()
    
    try:
        env = Environment(environment.lower())
    except ValueError:
        env = Environment.DEVELOPMENT
        logger = get_logger(__name__)
        logger.warning("Unknown environment, defaulting to development",
                      requested_environment=environment,
                      using_environment=env.value)
    
    # Load and apply environment configuration
    manager.load_and_apply_environment_config(env)
    
    # Start monitoring if enabled
    if enable_monitoring:
        manager.start_monitoring()
    
    logger = get_logger(__name__)
    logger.info("Logging system initialized",
               environment=env.value,
               service_name=service_name,
               monitoring_enabled=enable_monitoring,
               component="logging_initialization")


# Export main classes and functions
__all__ = [
    'LoggingConfigProfile',
    'ConfigurationValidator',
    'LoggingConfigurationManager',
    'LogLevel',
    'LogFormat',
    'Environment',
    'get_configuration_manager',
    'initialize_logging_for_environment'
]