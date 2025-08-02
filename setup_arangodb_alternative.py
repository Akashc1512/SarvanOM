from shared.core.api.config import get_settings
#!/usr/bin/env python3
settings = get_settings()
"""
ArangoDB Setup Script - Free Neo4j Alternative
This script helps set up ArangoDB as a free alternative to Neo4j.
"""

import os
import sys
import subprocess
import requests
import time
from typing import Dict, Any, Optional

def print_header():
    """Print setup header."""
    print("=" * 60)
    print("🆓 ARANGODB SETUP - FREE NEO4J ALTERNATIVE")
    print("=" * 60)
    print("ArangoDB is a free, multi-model database that supports")
    print("graph, document, and key-value data models.")
    print()

def check_system():
    """Check system requirements."""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check if ArangoDB is installed
    try:
        result = subprocess.run(['arangod', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ ArangoDB is already installed")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  ArangoDB not found - will provide installation instructions")
    
    return True

def get_installation_instructions():
    """Get installation instructions for different platforms."""
    print("\n📥 ARANGODB INSTALLATION INSTRUCTIONS")
    print("=" * 40)
    
    import platform
    system = platform.system().lower()
    
    if system == "windows":
        print("🪟 Windows Installation:")
        print("1. Download ArangoDB from: https://www.arangodb.com/download/")
        print("2. Run the installer (.exe file)")
        print("3. Follow the installation wizard")
        print("4. Start ArangoDB from Start Menu or:")
        print("   C:\\Program Files\\ArangoDB3\\usr\\bin\\arangod.exe")
        
    elif system == "darwin":  # macOS
        print("🍎 macOS Installation:")
        print("1. Install via Homebrew:")
        print("   brew install arangodb")
        print("2. Start ArangoDB:")
        print("   brew services start arangodb")
        print("3. Or download from: https://www.arangodb.com/download/")
        
    else:  # Linux
        print("🐧 Linux Installation:")
        print("1. Ubuntu/Debian:")
        print("   sudo apt-get update")
        print("   sudo apt-get install arangodb3")
        print("2. CentOS/RHEL:")
        print("   sudo yum install arangodb3")
        print("3. Or download from: https://www.arangodb.com/download/")
    
    print("\n🌐 After installation, access ArangoDB at:")
    print("   http://localhost:8529")
    print("   Default credentials: root / (empty password)")

def install_python_driver():
    """Install Python ArangoDB driver."""
    print("\n🐍 Installing Python ArangoDB driver...")
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'python-arango'], 
                      check=True, capture_output=True)
        print("✅ python-arango installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install python-arango: {e}")
        return False

def create_arangodb_agent():
    """Create an ArangoDB version of the KnowledgeGraphAgent."""
    print("\n🔧 Creating ArangoDB Knowledge Graph Agent...")
    
    agent_code = '''"""
ArangoDB Knowledge Graph Agent
Free alternative to Neo4j KnowledgeGraphAgent
"""

import asyncio
import logging
import time
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    from arango import ArangoClient
    ARANGO_AVAILABLE = True
except ImportError:
    ARANGO_AVAILABLE = False
    logging.warning("ArangoDB driver not available. Install with: pip install python-arango")

from shared.core.agents.base_agent import BaseAgent, AgentType, QueryContext, AgentResult
from shared.core.llm_client_v3 import EnhancedLLMClientV3

logger = logging.getLogger(__name__)


@dataclass
class EntityNode:
    """Represents an entity in the knowledge graph."""
    id: str
    name: str
    type: str
    properties: Dict[str, Any]
    confidence: float = 1.0


@dataclass
class Relationship:
    """Represents a relationship between entities."""
    source_id: str
    target_id: str
    relationship_type: str
    properties: Dict[str, Any]
    confidence: float = 1.0


@dataclass
class KnowledgeGraphResult:
    """Result from knowledge graph query."""
    entities: List[EntityNode]
    relationships: List[Relationship]
    paths: List[List[EntityNode]]
    query_entities: List[str]
    confidence: float
    processing_time_ms: float
    metadata: Dict[str, Any]


class ArangoDBKnowledgeGraphAgent(BaseAgent):
    """
    Agent for handling knowledge graph queries using ArangoDB.
    Free alternative to Neo4j KnowledgeGraphAgent.
    """
    
    def __init__(self):
        """Initialize the ArangoDB KnowledgeGraphAgent."""
        super().__init__("arangodb_knowledge_graph_agent", AgentType.RETRIEVAL)
        self.llm_client = EnhancedLLMClientV3()
        
        # ArangoDB connection configuration
        self.arango_url = settings.arango_url or "http://localhost:8529"
        self.arango_username = settings.arango_username or "root"
        self.arango_password = settings.arango_password or ""
        self.arango_database = settings.arango_database or "knowledge_graph"
        
        # ArangoDB client
        self.client: Optional[ArangoClient] = None
        self.db = None
        self.connected = False
        
        # Initialize connection if ArangoDB is available
        if ARANGO_AVAILABLE:
            asyncio.create_task(self._initialize_arangodb_connection())
        else:
            logger.warning("Using mock knowledge graph data - ArangoDB driver not available")
        
        # Initialize mock data as fallback
        self.mock_knowledge_graph = self._initialize_mock_knowledge_graph()
        
        logger.info("✅ ArangoDB KnowledgeGraphAgent initialized successfully")
    
    async def _initialize_arangodb_connection(self) -> None:
        """Initialize ArangoDB connection."""
        try:
            # Create ArangoDB client
            self.client = ArangoClient(hosts=self.arango_url)
            
            # Test connection
            await self._test_arangodb_connection()
            self.connected = True
            logger.info(f"✅ Connected to ArangoDB at {self.arango_url}")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to ArangoDB: {e}")
            self.connected = False
    
    async def _test_arangodb_connection(self) -> None:
        """Test ArangoDB connection."""
        try:
            # Test connection by getting server info
            self.db = self.client.db(
                name=self.arango_database,
                username=self.arango_username,
                password=self.arango_password
            )
            
            # Test with a simple query
            result = self.db.aql.execute("RETURN 1")
            if not result:
                raise ConnectionError("ArangoDB connection test failed")
                
        except Exception as e:
            raise ConnectionError(f"ArangoDB connection test failed: {e}")
    
    def _initialize_mock_knowledge_graph(self) -> Dict[str, Any]:
        """Initialize mock knowledge graph data for demonstration."""
        return {
            "entities": {
                "ml": {
                    "id": "ml",
                    "name": "Machine Learning",
                    "type": "technology",
                    "properties": {
                        "description": "A subset of artificial intelligence that enables systems to learn from data",
                        "category": "AI/ML",
                        "applications": ["prediction", "classification", "clustering"]
                    }
                },
                "ai": {
                    "id": "ai",
                    "name": "Artificial Intelligence",
                    "type": "technology",
                    "properties": {
                        "description": "The simulation of human intelligence by machines",
                        "category": "AI/ML",
                        "applications": ["automation", "decision_making", "problem_solving"]
                    }
                }
            },
            "relationships": [
                {
                    "source": "ml",
                    "target": "ai",
                    "type": "is_subset_of",
                    "properties": {
                        "description": "Machine Learning is a subset of Artificial Intelligence",
                        "confidence": 0.95
                    }
                }
            ]
        }
    
    async def query(self, query: str, query_type: str = "entity_relationship") -> KnowledgeGraphResult:
        """
        Query the knowledge graph using ArangoDB.
        
        Args:
            query: The query string
            query_type: Type of query (entity_relationship, path_finding, entity_search)
            
        Returns:
            KnowledgeGraphResult with entities, relationships, and paths
        """
        # Extract entities from query
        entities = await self._extract_entities(query)
        
        # Process based on query type
        if query_type == "entity_relationship":
            result = await self._process_entity_relationship_query(query, entities)
        elif query_type == "path_finding":
            result = await self._process_path_finding_query(query, entities)
        elif query_type == "entity_search":
            result = await self._process_entity_search_query(query, entities)
        else:
            result = await self._process_general_query(query, entities)
        
        return result
    
    async def _extract_entities(self, query: str) -> List[str]:
        """Extract entities from the query using LLM."""
        try:
            # Use LLM to extract entities
            prompt = f"""
            Extract the main entities (concepts, technologies, tools, people, organizations) from this query:
            "{query}"
            
            Return only the entity names, one per line, without explanations.
            """
            
            response = await self.llm_client.generate_text(prompt, max_tokens=50)
            entities = [line.strip() for line in response.strip().split('\\n') if line.strip()]
            
            logger.info(f"Extracted entities: {entities}")
            return entities
            
        except Exception as e:
            logger.warning(f"Entity extraction failed: {e}")
            # Fallback: simple keyword extraction
            keywords = ["machine learning", "artificial intelligence", "deep learning", 
                       "neural networks", "python", "javascript", "react", "docker", 
                       "kubernetes", "blockchain", "cloud computing"]
            
            found_entities = []
            query_lower = query.lower()
            for keyword in keywords:
                if keyword in query_lower:
                    found_entities.append(keyword)
            
            return found_entities
    
    async def _process_entity_relationship_query(self, query: str, entities: List[str]) -> KnowledgeGraphResult:
        """Process entity-relationship queries using ArangoDB."""
        if self.connected and self.db:
            return await self._query_arangodb_entity_relationships(query, entities)
        else:
            return await self._query_mock_entity_relationships(query, entities)
    
    async def _process_path_finding_query(self, query: str, entities: List[str]) -> KnowledgeGraphResult:
        """Process path-finding queries using ArangoDB."""
        if self.connected and self.db:
            return await self._query_arangodb_path_finding(query, entities)
        else:
            return await self._query_mock_path_finding(query, entities)
    
    async def _process_entity_search_query(self, query: str, entities: List[str]) -> KnowledgeGraphResult:
        """Process entity search queries using ArangoDB."""
        if self.connected and self.db:
            return await self._query_arangodb_entity_search(query, entities)
        else:
            return await self._query_mock_entity_search(query, entities)
    
    async def _process_general_query(self, query: str, entities: List[str]) -> KnowledgeGraphResult:
        """Process general knowledge graph queries using ArangoDB."""
        if self.connected and self.db:
            return await self._query_arangodb_general(query, entities)
        else:
            return await self._query_mock_general(query, entities)
    
    # ArangoDB Query Methods
    async def _query_arangodb_entity_relationships(self, query: str, entities: List[str]) -> KnowledgeGraphResult:
        """Query ArangoDB for entity relationships."""
        try:
            if len(entities) < 2:
                # Single entity query
                aql_query = """
                FOR doc IN entities
                FILTER CONTAINS(LOWER(doc.name), LOWER(@entity)) OR CONTAINS(LOWER(doc.id), LOWER(@entity))
                RETURN doc
                LIMIT 20
                """
                parameters = {"entity": entities[0] if entities else ""}
            else:
                # Multiple entities - find relationships between them
                aql_query = """
                FOR rel IN relationships
                FOR entity1 IN entities
                FOR entity2 IN entities
                FILTER rel._from == entity1._id AND rel._to == entity2._id
                FILTER (CONTAINS(LOWER(entity1.name), LOWER(@entity1)) OR CONTAINS(LOWER(entity1.id), LOWER(@entity1)))
                AND (CONTAINS(LOWER(entity2.name), LOWER(@entity2)) OR CONTAINS(LOWER(entity2.id), LOWER(@entity2)))
                RETURN {entity1, rel, entity2}
                LIMIT 20
                """
                parameters = {
                    "entity1": entities[0],
                    "entity2": entities[1]
                }
            
            result = self.db.aql.execute(aql_query, parameters)
            
            # Parse results
            found_entities = []
            found_relationships = []
            
            for record in result:
                if 'entity1' in record:
                    entity = record['entity1']
                    found_entities.append(EntityNode(
                        id=entity.get('id', ''),
                        name=entity.get('name', ''),
                        type=entity.get('type', 'Node'),
                        properties=entity
                    ))
                if 'entity2' in record:
                    entity = record['entity2']
                    found_entities.append(EntityNode(
                        id=entity.get('id', ''),
                        name=entity.get('name', ''),
                        type=entity.get('type', 'Node'),
                        properties=entity
                    ))
                
                if 'rel' in record:
                    rel = record['rel']
                    found_relationships.append(Relationship(
                        source_id=rel.get('_from', ''),
                        target_id=rel.get('_to', ''),
                        relationship_type=rel.get('type', ''),
                        properties=rel
                    ))
            
            return KnowledgeGraphResult(
                entities=found_entities,
                relationships=found_relationships,
                paths=[],
                query_entities=entities,
                confidence=0.9 if found_entities else 0.3,
                processing_time_ms=0,
                metadata={
                    "query_type": "entity_relationship",
                    "entities_found": len(found_entities),
                    "relationships_found": len(found_relationships),
                    "arangodb_query": aql_query
                }
            )
            
        except Exception as e:
            logger.error(f"ArangoDB entity relationship query failed: {e}")
            return KnowledgeGraphResult(
                entities=[],
                relationships=[],
                paths=[],
                query_entities=entities,
                confidence=0.0,
                processing_time_ms=0,
                metadata={"error": str(e)}
            )
    
    # Mock Query Methods (fallback)
    async def _query_mock_entity_relationships(self, query: str, entities: List[str]) -> KnowledgeGraphResult:
        """Process entity-relationship queries using mock data."""
        found_entities = []
        found_relationships = []
        
        # Find entities in knowledge graph
        for entity_name in entities:
            for entity_id, entity_data in self.mock_knowledge_graph["entities"].items():
                if entity_name.lower() in entity_data["name"].lower() or entity_name.lower() in entity_id:
                    found_entities.append(EntityNode(
                        id=entity_id,
                        name=entity_data["name"],
                        type=entity_data["type"],
                        properties=entity_data["properties"]
                    ))
        
        # Find relationships involving these entities
        for rel in self.mock_knowledge_graph["relationships"]:
            source_entity = next((e for e in found_entities if e.id == rel["source"]), None)
            target_entity = next((e for e in found_entities if e.id == rel["target"]), None)
            
            if source_entity and target_entity:
                found_relationships.append(Relationship(
                    source_id=rel["source"],
                    target_id=rel["target"],
                    relationship_type=rel["type"],
                    properties=rel["properties"]
                ))
        
        return KnowledgeGraphResult(
            entities=found_entities,
            relationships=found_relationships,
            paths=[],
            query_entities=entities,
            confidence=0.85 if found_entities else 0.3,
            processing_time_ms=0,
            metadata={
                "query_type": "entity_relationship",
                "entities_found": len(found_entities),
                "relationships_found": len(found_relationships),
                "mock_data": True
            }
        )
    
    async def _query_mock_path_finding(self, query: str, entities: List[str]) -> KnowledgeGraphResult:
        """Process path-finding queries using mock data."""
        return await self._query_mock_entity_relationships(query, entities)
    
    async def _query_mock_entity_search(self, query: str, entities: List[str]) -> KnowledgeGraphResult:
        """Process entity search queries using mock data."""
        return await self._query_mock_entity_relationships(query, entities)
    
    async def _query_mock_general(self, query: str, entities: List[str]) -> KnowledgeGraphResult:
        """Process general knowledge graph queries using mock data."""
        return await self._query_mock_entity_relationships(query, entities)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the ArangoDB knowledge graph agent."""
        return {
            "status": "healthy" if self.connected else "disconnected",
            "agent_type": "arangodb_knowledge_graph",
            "arangodb_connected": self.connected,
            "arangodb_url": self.arango_url,
            "entities_count": len(self.mock_knowledge_graph["entities"]) if hasattr(self, 'mock_knowledge_graph') else 0,
            "relationships_count": len(self.mock_knowledge_graph["relationships"]) if hasattr(self, 'mock_knowledge_graph') else 0,
            "last_updated": datetime.now().isoformat()
        }
'''
    
    # Write the agent code to a file
    with open('shared/core/agents/arangodb_knowledge_graph_agent.py', 'w') as f:
        f.write(agent_code)
    
    print("✅ ArangoDB Knowledge Graph Agent created at:")
    print("   shared/core/agents/arangodb_knowledge_graph_agent.py")

def update_env_template():
    """Update env.template with ArangoDB configuration."""
    print("\n🔧 Updating environment template...")
    
    arango_config = '''
# =============================================================================
# ARANGODB KNOWLEDGE GRAPH CONFIGURATION (FREE NEO4J ALTERNATIVE)
# =============================================================================
ARANGO_URL=http://localhost:8529
ARANGO_USERNAME=root
ARANGO_PASSWORD=
ARANGO_DATABASE=knowledge_graph
'''
    
    # Read current env.template
    try:
        with open('env.template', 'r') as f:
            content = f.read()
        
        # Add ArangoDB configuration after Neo4j section
        if 'NEO4J_API_KEY=' in content:
            # Insert after Neo4j section
            content = content.replace('NEO4J_API_KEY=', 'NEO4J_API_KEY=\n' + arango_config)
        else:
            # Add at the end
            content += arango_config
        
        # Write back
        with open('env.template', 'w') as f:
            f.write(content)
        
        print("✅ Environment template updated with ArangoDB configuration")
        
    except Exception as e:
        print(f"❌ Failed to update env.template: {e}")

def create_test_script():
    """Create a test script for ArangoDB agent."""
    print("\n🧪 Creating ArangoDB test script...")
    
    test_code = '''#!/usr/bin/env python3
"""
Test script for ArangoDB KnowledgeGraphAgent
Free alternative to Neo4j KnowledgeGraphAgent
"""

import asyncio
import logging
import os
import sys
from typing import Dict, Any

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared.core.agents.arangodb_knowledge_graph_agent import ArangoDBKnowledgeGraphAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_arangodb_agent():
    """Test the ArangoDB KnowledgeGraphAgent."""
    
    print("🧪 Testing ArangoDB KnowledgeGraphAgent")
    print("=" * 50)
    
    # Initialize the agent
    agent = ArangoDBKnowledgeGraphAgent()
    
    # Wait a moment for ArangoDB connection to initialize
    await asyncio.sleep(2)
    
    # Test queries
    test_queries = [
        {
            "query": "How is machine learning related to artificial intelligence?",
            "type": "entity_relationship",
            "description": "Entity relationship query"
        },
        {
            "query": "Tell me about Docker",
            "type": "entity_search",
            "description": "Entity search query"
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\\n🔍 Test {i}: {test_case['description']}")
        print(f"Query: {test_case['query']}")
        print(f"Type: {test_case['type']}")
        print("-" * 30)
        
        try:
            # Execute query
            result = await agent.query(test_case['query'], test_case['type'])
            
            # Display results
            print(f"✅ Query completed successfully")
            print(f"Confidence: {result.confidence:.2f}")
            print(f"Processing time: {result.processing_time_ms:.2f}ms")
            print(f"Entities found: {len(result.entities)}")
            print(f"Relationships found: {len(result.relationships)}")
            print(f"Paths found: {len(result.paths)}")
            
            # Display entities
            if result.entities:
                print("\\n📋 Entities:")
                for entity in result.entities[:5]:  # Show first 5
                    print(f"  - {entity.name} ({entity.type})")
                    if entity.properties.get('description'):
                        print(f"    Description: {entity.properties['description'][:100]}...")
            
            # Display relationships
            if result.relationships:
                print("\\n🔗 Relationships:")
                for rel in result.relationships[:5]:  # Show first 5
                    print(f"  - {rel.source_id} --[{rel.relationship_type}]--> {rel.target_id}")
                    if rel.properties.get('description'):
                        print(f"    Description: {rel.properties['description']}")
            
            # Display metadata
            if result.metadata:
                print(f"\\n📊 Metadata:")
                for key, value in result.metadata.items():
                    if key not in ['entities_found', 'relationships_found', 'paths_found']:
                        print(f"  {key}: {value}")
            
        except Exception as e:
            print(f"❌ Query failed: {e}")
        
        print("\\n" + "=" * 50)
    
    # Test health status
    print("\\n🏥 Health Status:")
    health = agent.get_health_status()
    for key, value in health.items():
        print(f"  {key}: {value}")
    
    print("\\n✅ ArangoDB KnowledgeGraphAgent test completed!")


async def test_arangodb_connection():
    """Test ArangoDB connection specifically."""
    
    print("\\n🔌 Testing ArangoDB Connection")
    print("=" * 30)
    
    # Check environment variables
    arango_vars = {
        "ARANGO_URL": settings.arango_url,
        "ARANGO_USERNAME": settings.arango_username,
        "ARANGO_PASSWORD": settings.arango_password,
        "ARANGO_DATABASE": settings.arango_database
    }
    
    print("Environment Variables:")
    for key, value in arango_vars.items():
        if key == "ARANGO_PASSWORD" and value:
            print(f"  {key}: {'*' * len(value)}")
        else:
            print(f"  {key}: {value or 'Not set'}")
    
    # Initialize agent
    agent = ArangoDBKnowledgeGraphAgent()
    await asyncio.sleep(2)
    
    print(f"\\nArangoDB Connection Status: {'✅ Connected' if agent.connected else '❌ Disconnected'}")
    print(f"Using Mock Data: {not agent.connected}")
    
    if agent.connected:
        print("✅ ArangoDB is available and connected!")
    else:
        print("⚠️  ArangoDB is not available. Using mock data for testing.")
        print("To enable ArangoDB:")
        print("  1. Install ArangoDB: https://www.arangodb.com/download/")
        print("  2. Start ArangoDB server")
        print("  3. Set environment variables: ARANGO_URL, ARANGO_USERNAME, ARANGO_PASSWORD")


def main():
    """Main function to run the tests."""
    print("🚀 Starting ArangoDB KnowledgeGraphAgent Tests")
    print("=" * 60)
    
    try:
        # Run tests
        asyncio.run(test_arangodb_connection())
        asyncio.run(test_arangodb_agent())
        
    except KeyboardInterrupt:
        print("\\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\\n❌ Test failed with error: {e}")
        logger.exception("Test failed")


if __name__ == "__main__":
    main()
'''
    
    # Write the test script
    with open('test_arangodb_agent.py', 'w') as f:
        f.write(test_code)
    
    print("✅ ArangoDB test script created at:")
    print("   test_arangodb_agent.py")

def main():
    """Main setup function."""
    print_header()
    
    # Check system requirements
    if not check_system():
        print("❌ System requirements not met. Please fix the issues above.")
        return
    
    # Get installation instructions
    get_installation_instructions()
    
    # Install Python driver
    if install_python_driver():
        print("✅ Python ArangoDB driver installed successfully")
    else:
        print("❌ Failed to install Python driver")
        return
    
    # Create ArangoDB agent
    create_arangodb_agent()
    
    # Update environment template
    update_env_template()
    
    # Create test script
    create_test_script()
    
    print("\n" + "=" * 60)
    print("🎉 ARANGODB SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("📋 Next Steps:")
    print("1. Install ArangoDB using the instructions above")
    print("2. Start ArangoDB server")
    print("3. Set environment variables in .env:")
    print("   ARANGO_URL=http://localhost:8529")
    print("   ARANGO_USERNAME=root")
    print("   ARANGO_PASSWORD=")
    print("   ARANGO_DATABASE=knowledge_graph")
    print("4. Test the setup:")
    print("   python test_arangodb_agent.py")
    print()
    print("🌐 Access ArangoDB web interface at: http://localhost:8529")
    print("   Default credentials: root / (empty password)")
    print()
    print("✅ You now have a free alternative to Neo4j!")


if __name__ == "__main__":
    main() 