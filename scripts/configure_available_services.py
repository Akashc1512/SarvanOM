from ..\shared\core\api\config import get_settings
#!/usr/bin/env python3
settings = get_settings()
"""
Configure Available Services Script.

This script helps configure the application to use only the services
that are actually available, disabling those that aren't needed.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_service_availability() -> Dict[str, bool]:
    """Check which services are actually available."""
    services = {}
    
    # Check Redis
    redis_url = settings.redis_url or ''
    if redis_url and not any(p in redis_url for p in ['your-', 'change-', 'placeholder']):
        # Fix Redis URL format if needed
        if redis_url.startswith('clustercfg.'):
            # AWS ElastiCache format
            services['redis'] = {
                'available': True,
                'url': f"redis://{redis_url}",
                'note': "Fixed Redis URL format for AWS ElastiCache"
            }
        elif redis_url.startswith('redis://'):
            services['redis'] = {
                'available': True,
                'url': redis_url,
                'note': "Redis URL properly formatted"
            }
        else:
            services['redis'] = {
                'available': False,
                'url': redis_url,
                'note': "Invalid Redis URL format"
            }
    else:
        services['redis'] = {
            'available': False,
            'url': None,
            'note': "Redis not configured"
        }
    
    # Check Meilisearch
    meili_url = settings.meilisearch_url or ''
    if meili_url and not any(p in meili_url for p in ['your-', 'change-', 'placeholder']):
        # Remove quotes if present
        meili_url = meili_url.strip('"\'')
        services['meilisearch'] = {
            'available': True,
            'url': meili_url,
            'note': "Meilisearch configured"
        }
    else:
        services['meilisearch'] = {
            'available': False,
            'url': None,
            'note': "Meilisearch not configured"
        }
    
    # Check Pinecone
    pinecone_key = settings.pinecone_api_key or ''
    if pinecone_key and not any(p in pinecone_key for p in ['your-', 'change-', 'placeholder']):
        services['pinecone'] = {
            'available': True,
            'note': "Pinecone API key configured"
        }
    else:
        services['pinecone'] = {
            'available': False,
            'note': "Pinecone not configured"
        }
    
    # Check Qdrant
    qdrant_url = settings.qdrant_url or ''
    if qdrant_url and not any(p in qdrant_url for p in ['your-', 'change-', 'placeholder']):
        services['qdrant'] = {
            'available': True,
            'url': qdrant_url,
            'note': "Qdrant configured"
        }
    else:
        services['qdrant'] = {
            'available': False,
            'note': "Qdrant not configured"
        }
    
    # Check ArangoDB
    arango_url = settings.arango_url or ''
    if arango_url and not any(p in arango_url for p in ['your-', 'change-', 'placeholder']):
        services['arangodb'] = {
            'available': True,
            'url': arango_url,
            'note': "ArangoDB configured"
        }
    else:
        services['arangodb'] = {
            'available': False,
            'url': None,
            'note': "ArangoDB not configured"
        }
    
    return services

def generate_config_overrides(services: Dict[str, bool]) -> Dict[str, any]:
    """Generate configuration overrides based on available services."""
    config = {
        'services': {
            'redis': {
                'enabled': services.get('redis', {}).get('available', False),
                'url': services.get('redis', {}).get('url', None)
            },
            'meilisearch': {
                'enabled': services.get('meilisearch', {}).get('available', False),
                'url': services.get('meilisearch', {}).get('url', None)
            },
            'pinecone': {
                'enabled': services.get('pinecone', {}).get('available', False)
            },
            'qdrant': {
                'enabled': services.get('qdrant', {}).get('available', False),
                'url': services.get('qdrant', {}).get('url', None)
            },
            'arangodb': {
                'enabled': services.get('arangodb', {}).get('available', False),
                'url': services.get('arangodb', {}).get('url', None)
            }
        },
        'features': {
            'caching': services.get('redis', {}).get('available', False),
            'vector_search': any([
                services.get('pinecone', {}).get('available', False),
                services.get('qdrant', {}).get('available', False),
                services.get('meilisearch', {}).get('available', False)
            ]),
            'knowledge_graph': services.get('arangodb', {}).get('available', False)
        }
    }
    
    return config

def create_service_config_file(config: Dict[str, any]):
    """Create a service configuration file."""
    config_path = Path('config/services.json')
    config_path.parent.mkdir(exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Created service configuration at: {config_path}")

def generate_env_updates(services: Dict[str, bool]) -> List[str]:
    """Generate .env updates for service URLs."""
    updates = []
    
    # Fix Redis URL if needed
    if services.get('redis', {}).get('available') and 'Fixed Redis URL' in services['redis'].get('note', ''):
        updates.append(f"REDIS_URL={services['redis']['url']}")
    
    # Fix Elasticsearch URL if needed
    if services.get('elasticsearch', {}).get('available'):
        es_url = services['elasticsearch'].get('url', '').strip('"\'')
        if es_url != os.getenv('ELASTICSEARCH_URL'):
            updates.append(f'ELASTICSEARCH_URL={es_url}')
    
    return updates

def main():
    """Main configuration function."""
    print("SERVICE AVAILABILITY CONFIGURATION")
    print("="*60)
    
    # Check service availability
    services = check_service_availability()
    
    print("\nSERVICE STATUS:")
    print("-"*40)
    for service_name, info in services.items():
        status = "✅" if info.get('available') else "❌"
        print(f"{status} {service_name.upper()}: {info.get('note')}")
    
    # Generate configuration
    config = generate_config_overrides(services)
    
    print("\nCONFIGURATION SUMMARY:")
    print("-"*40)
    print(f"Caching: {'Enabled' if config['features']['caching'] else 'Disabled'}")
    print(f"Vector Search: {'Enabled' if config['features']['vector_search'] else 'Disabled'}")
    print(f"Knowledge Graph: {'Enabled' if config['features']['knowledge_graph'] else 'Disabled'}")
    
    # Create configuration file
    create_service_config_file(config)
    
    # Generate .env updates
    env_updates = generate_env_updates(services)
    if env_updates:
        print("\nRECOMMENDED .ENV UPDATES:")
        print("-"*40)
        print("Add or update these lines in your .env file:")
        for update in env_updates:
            print(f"  {update}")
    
    # Provide recommendations
    print("\nRECOMMENDATIONS:")
    print("-"*40)
    
    if not config['features']['vector_search']:
        print("⚠️  No vector database configured. Consider setting up:")
        print("   - Pinecone (cloud-based, easy setup)")
        print("   - Qdrant (self-hosted or cloud)")
        print("   - Meilisearch (if you already have it)")
    
    if not config['features']['caching']:
        print("⚠️  No caching configured. Consider setting up Redis for better performance.")
    
    if services.get('redis', {}).get('available') and 'Fixed' in services['redis'].get('note', ''):
        print("⚠️  Redis URL format was incorrect. Update your .env with the fixed URL above.")
    
    print("\n✅ Configuration complete! The application will use only available services.")
    print("   Services not configured will be gracefully disabled.")

if __name__ == '__main__':
    main() 