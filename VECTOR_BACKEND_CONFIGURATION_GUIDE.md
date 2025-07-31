# Vector Backend Configuration Guide

## 🔍 **Current Status Summary**

### ✅ **Working Services:**
- **Pinecone**: Fully operational ✅
- **Redis**: Fully operational ✅

### ⚠️ **Authentication Issues:**
- **Elasticsearch**: 401 Authentication Error
- **Qdrant**: 403 Forbidden Error  
- **Neo4j**: Unauthorized Error

---

## 🔧 **Elasticsearch Authentication Fix**

### **Issue:** `AuthenticationException(401, 'security_exception', 'missing authentication credentials')`

### **Solution:**

1. **Update your `.env` file with proper authentication:**

```bash
# Elasticsearch Configuration
ELASTICSEARCH_URL=https://07edb47f1d154aefa7fd1cc0d519cbbe.us-east-1.aws.found.io:443
ELASTICSEARCH_API_KEY=your_elasticsearch_api_key_here
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=your_elasticsearch_password_here
ELASTICSEARCH_INDEX=sarvanom-elastic
```

2. **For Elastic Cloud, you need either:**
   - **API Key** (preferred): Get from Elastic Cloud console
   - **Username/Password**: Use your Elastic Cloud credentials

3. **Test the connection:**
```bash
curl -H "Authorization: ApiKey YOUR_API_KEY" https://07edb47f1d154aefa7fd1cc0d519cbbe.us-east-1.aws.found.io:443
```

---

## 🔧 **Qdrant Authentication Fix**

### **Issue:** `403 Forbidden`

### **Solution:**

1. **Update your `.env` file:**

```bash
# Qdrant Configuration
QDRANT_URL=https://cba0029b-4ca1-4a72-bd69-e4dc682385ef.us-west-1-0.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION=knowledge-base
```

2. **For Qdrant Cloud, you need:**
   - **API Key**: Get from Qdrant Cloud console
   - **URL**: Your Qdrant Cloud instance URL

3. **Test the connection:**
```bash
curl -H "api-key: YOUR_API_KEY" https://cba0029b-4ca1-4a72-bd69-e4dc682385ef.us-west-1-0.aws.cloud.qdrant.io:6333/collections
```

---

## 🔧 **Neo4j Authentication Fix**

### **Issue:** `Neo.ClientError.Security.Unauthorized`

### **Solution:**

1. **Update your `.env` file:**

```bash
# Neo4j Configuration
NEO4J_URI=neo4j+s://a0cd8cf2.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password_here
NEO4J_DATABASE=neo4j
AURA_INSTANCEID=a0cd8cf2
AURA_INSTANCENAME=Instance01
```

2. **For Neo4j Aura, you need:**
   - **Password**: Your Aura database password
   - **URI**: Your Aura instance URI
   - **Username**: Usually `neo4j`

3. **Test the connection:**
```bash
cypher-shell -u neo4j -p YOUR_PASSWORD -a neo4j+s://a0cd8cf2.databases.neo4j.io
```

---

## 🚀 **Quick Fix Commands**

### **1. Test Elasticsearch:**
```bash
curl -H "Authorization: ApiKey YOUR_API_KEY" https://07edb47f1d154aefa7fd1cc0d519cbbe.us-east-1.aws.found.io:443
```

### **2. Test Qdrant:**
```bash
curl -H "api-key: YOUR_API_KEY" https://cba0029b-4ca1-4a72-bd69-e4dc682385ef.us-west-1-0.aws.cloud.qdrant.io:6333/collections
```

### **3. Test Neo4j:**
```bash
cypher-shell -u neo4j -p YOUR_PASSWORD -a neo4j+s://a0cd8cf2.databases.neo4j.io -c "RETURN 1 as test"
```

### **4. Re-run Vector Backend Check:**
```bash
python scripts/check_vector_backends.py
```

---

## 📋 **Environment Variables Checklist**

Make sure your `.env` file contains:

```bash
# Vector Database Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=ukp-knowledge-base
VECTOR_DB_HOST=https://ukp-knowledge-base-07whq52.svc.aped-4627-b74a.pinecone.io

# Qdrant Configuration
QDRANT_URL=https://cba0029b-4ca1-4a72-bd69-e4dc682385ef.us-west-1-0.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=your_qdrant_api_key_here

# Elasticsearch Configuration
ELASTICSEARCH_URL=https://07edb47f1d154aefa7fd1cc0d519cbbe.us-east-1.aws.found.io:443
ELASTICSEARCH_API_KEY=your_elasticsearch_api_key_here
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=your_elasticsearch_password_here
ELASTICSEARCH_INDEX=sarvanom-elastic

# Neo4j Configuration
NEO4J_URI=neo4j+s://a0cd8cf2.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password_here
NEO4J_DATABASE=neo4j
AURA_INSTANCEID=a0cd8cf2
AURA_INSTANCENAME=Instance01

# Redis Configuration
REDIS_URL=redis://clustercfg.ukp-redis.adjkvz.use1.cache.amazonaws.com:6379
```

---

## 🎯 **Next Steps**

1. **Get the missing API keys/passwords** from your cloud providers
2. **Update your `.env` file** with the correct credentials
3. **Test each service individually** using the curl commands above
4. **Re-run the vector backend checker** to verify all services are working
5. **Start your backend server** once all services are operational

---

## 📞 **Support**

If you need help getting the API keys or passwords:
- **Elasticsearch**: Check your Elastic Cloud console
- **Qdrant**: Check your Qdrant Cloud console  
- **Neo4j**: Check your Aura console

Once you have the correct credentials, update your `.env` file and re-run the vector backend checker! 