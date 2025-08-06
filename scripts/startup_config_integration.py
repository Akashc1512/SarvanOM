#!/usr/bin/env python3
"""
Startup Configuration Integration Script

This script demonstrates how to integrate the enhanced environment manager
into application startup with proper validation and error handling.

This can be used as a template for main.py files in your services.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def initialize_application_config():
    """
    Initialize application configuration with enhanced validation.
    
    This function should be called at the very beginning of your application startup,
    before any other imports or initialization.
    
    Returns:
        tuple: (success: bool, manager: EnhancedEnvironmentManager or None, error: str or None)
    """
    try:
        print("🚀 Initializing application configuration...")
        
        # Import enhanced environment manager
        from shared.core.config.enhanced_environment_manager import (
            get_enhanced_environment_manager,
            validate_environment_on_startup
        )
        
        # Get current environment
        app_env = os.getenv("APP_ENV", "development")
        print(f"🌍 Environment: {app_env.upper()}")
        
        # Initialize enhanced manager (this will validate configuration)
        manager = get_enhanced_environment_manager()
        print(f"✅ Configuration manager initialized")
        
        # Perform full startup validation
        print("🔍 Performing startup validation...")
        validation_success = validate_environment_on_startup()
        
        if not validation_success:
            return False, None, "Startup validation failed - check logs for details"
        
        print("✅ Startup validation passed")
        
        # Log configuration summary (this is automatically done by the manager)
        config = manager.get_config()
        
        return True, manager, None
        
    except ValueError as e:
        # Configuration validation errors
        error_msg = f"Configuration validation failed: {e}"
        print(f"❌ {error_msg}")
        return False, None, error_msg
        
    except ImportError as e:
        # Missing dependencies
        error_msg = f"Configuration modules not available: {e}"
        print(f"❌ {error_msg}")
        return False, None, error_msg
        
    except Exception as e:
        # Unexpected errors
        error_msg = f"Unexpected configuration error: {e}"
        print(f"❌ {error_msg}")
        return False, None, error_msg


def demonstrate_configuration_usage(manager):
    """Demonstrate how to use the configuration manager in your application."""
    
    print("\n📋 Configuration Usage Examples:")
    print("-" * 50)
    
    config = manager.get_config()
    
    # Environment checks
    print(f"🌍 Environment checks:")
    print(f"   Is production: {manager.is_production()}")
    print(f"   Is development: {manager.is_development()}")
    print(f"   Is testing: {manager.is_testing()}")
    
    # Feature flags
    print(f"\n🎛️  Feature flags:")
    print(f"   Streaming enabled: {manager.get_feature('streaming')}")
    print(f"   Admin panel enabled: {manager.get_feature('admin_panel')}")
    print(f"   Real-time collaboration: {manager.get_feature('real_time_collaboration')}")
    
    # Secret access (safe - doesn't log actual values)
    print(f"\n🔐 Secret access:")
    jwt_secret = manager.get_secret("JWT_SECRET_KEY")
    print(f"   JWT secret configured: {'Yes' if jwt_secret else 'No'}")
    
    openai_key = manager.get_secret("OPENAI_API_KEY")
    print(f"   OpenAI key configured: {'Yes' if openai_key else 'No'}")
    
    # Performance settings
    print(f"\n⚡ Performance settings:")
    print(f"   Worker processes: {config.worker_processes}")
    print(f"   Worker threads: {config.worker_threads}")
    print(f"   DB pool size: {config.db_pool_size}")
    print(f"   Rate limit: {config.rate_limit_per_minute}/min")


def demonstrate_error_handling():
    """Demonstrate proper error handling for configuration issues."""
    
    print("\n🧪 Testing Error Handling:")
    print("-" * 50)
    
    # Test with invalid environment
    original_env = os.getenv("APP_ENV")
    
    try:
        # Test invalid environment
        print("🧪 Testing invalid environment...")
        os.environ["APP_ENV"] = "invalid_env"
        
        # Clear any cached manager
        import shared.core.config.enhanced_environment_manager as env_module
        env_module._enhanced_manager = None
        
        success, manager, error = initialize_application_config()
        
        if not success:
            print(f"✅ Error properly caught: {error}")
        else:
            print(f"⚠️  Expected error but got success")
            
    finally:
        # Restore original environment
        if original_env:
            os.environ["APP_ENV"] = original_env
        else:
            os.environ.pop("APP_ENV", None)
        
        # Clear cached manager
        env_module._enhanced_manager = None


def demonstrate_environment_switching():
    """Demonstrate switching between environments."""
    
    print("\n🔄 Environment Switching Demo:")
    print("-" * 50)
    
    environments = ["development", "testing", "staging"]
    original_env = os.getenv("APP_ENV")
    
    try:
        for env in environments:
            print(f"\n🌍 Switching to {env} environment...")
            os.environ["APP_ENV"] = env
            
            # Clear cached manager to force reload
            import shared.core.config.enhanced_environment_manager as env_module
            env_module._enhanced_manager = None
            
            try:
                success, manager, error = initialize_application_config()
                
                if success:
                    config = manager.get_config()
                    print(f"   ✅ {env}: Debug={config.debug}, LogLevel={config.log_level}")
                else:
                    print(f"   ❌ {env}: {error}")
                    
            except Exception as e:
                print(f"   ❌ {env}: {e}")
    
    finally:
        # Restore original environment
        if original_env:
            os.environ["APP_ENV"] = original_env
        else:
            os.environ.pop("APP_ENV", None)


def main():
    """Main demonstration function."""
    
    print("🔧 Configuration Management Integration Demo")
    print("=" * 80)
    
    # Initialize configuration
    success, manager, error = initialize_application_config()
    
    if not success:
        print(f"\n💥 Configuration initialization failed!")
        print(f"Error: {error}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Check that APP_ENV is set to a valid environment")
        print("2. Ensure all required environment variables are set")
        print("3. Verify configuration files exist")
        print("4. Run: python scripts/verify_env_config.py")
        return 1
    
    print(f"\n🎉 Configuration successfully initialized!")
    
    # Demonstrate usage
    demonstrate_configuration_usage(manager)
    
    # Demonstrate error handling
    demonstrate_error_handling()
    
    # Demonstrate environment switching
    demonstrate_environment_switching()
    
    print("\n" + "=" * 80)
    print("✅ Configuration integration demo completed successfully!")
    print("💡 Use this pattern in your main.py files for robust configuration handling")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())