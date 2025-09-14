# SarvanOM Comprehensive Testing Framework

This directory contains a comprehensive testing framework for the SarvanOM microservices platform, including load testing, user acceptance testing, performance monitoring, and production deployment simulation.

## 🎯 Overview

The testing framework is designed to validate the SarvanOM platform across multiple dimensions:

- **Load Testing**: Validate system performance under various load conditions
- **User Acceptance Testing**: Ensure business requirements are met
- **Performance Monitoring**: Real-time performance tracking and SLA validation
- **Production Deployment**: Simulate production deployment scenarios

## 📁 Directory Structure

```
├── load_testing/
│   ├── load_test_framework.py      # Core load testing framework
│   ├── service_specific_tests.py   # Service-specific load tests
│   └── performance_monitor.py      # Performance monitoring and SLA tracking
├── user_acceptance_testing/
│   └── uat_framework.py           # User acceptance testing framework
├── operations/
│   └── deployment_pipeline.py     # Production deployment simulation
├── run_comprehensive_testing.py   # Main testing orchestrator
├── requirements_testing.txt       # Testing dependencies
└── TESTING_README.md             # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_testing.txt
```

### 2. Ensure Services Are Running

Make sure all SarvanOM services are running on their expected ports:

- Model Registry: `http://localhost:8000`
- Gateway: `http://localhost:8007`
- Synthesis: `http://localhost:8008`
- Feeds: `http://localhost:8005`
- Retrieval: `http://localhost:8004`
- Auth: `http://localhost:8012`
- Knowledge Graph: `http://localhost:8013`
- Search: `http://localhost:8015`
- And all other services...

### 3. Run Comprehensive Testing

```bash
# Run all testing phases
python run_comprehensive_testing.py

# Run specific phases
python run_comprehensive_testing.py --phase=load
python run_comprehensive_testing.py --phase=uat
python run_comprehensive_testing.py --phase=performance
python run_comprehensive_testing.py --phase=deployment

# Enable verbose logging
python run_comprehensive_testing.py --verbose
```

## 📊 Testing Phases

### 1. Load Testing

**Purpose**: Validate system performance under various load conditions

**Features**:
- Concurrent user simulation
- Service-specific load tests
- Performance metrics collection
- Stress testing scenarios
- Real-time monitoring integration

**Test Scenarios**:
- Light load (5 users, 30 seconds)
- Medium load (20 users, 60 seconds)
- Heavy load (50 users, 120 seconds)
- Stress testing (200 users, 120 seconds)

**Key Metrics**:
- Requests per second
- Response times (avg, min, max, p95, p99)
- Success/failure rates
- System resource usage

### 2. User Acceptance Testing (UAT)

**Purpose**: Ensure business requirements are met and system works as expected

**Test Scenarios**:
- Health Check Validation
- News Feed Processing
- Model Registry Operations
- Configuration Management
- Authentication Service
- Multi-Service Integration
- Performance Validation
- Error Handling

**Validation Criteria**:
- All services healthy and responding
- End-to-end workflows functional
- Response times within acceptable limits
- Proper error handling and graceful degradation

### 3. Performance Monitoring

**Purpose**: Real-time performance tracking and SLA validation

**Features**:
- Continuous service monitoring
- SLA compliance checking
- Performance metrics collection
- Alert generation for violations
- Historical performance analysis

**SLA Benchmarks**:
- Health endpoints: <100ms response time, 99.9% success rate
- Data processing: <5s response time, 95% success rate
- Config endpoints: <500ms response time, 99% success rate

### 4. Production Deployment Simulation

**Purpose**: Simulate production deployment scenarios

**Features**:
- Automated service deployment
- Health check validation
- Rollback capabilities
- Deployment monitoring
- Service status tracking

## 📈 Performance Benchmarks

### Response Time Targets

| Service Type | Endpoint | Target Response Time | Success Rate |
|--------------|----------|---------------------|--------------|
| Health Checks | `/health` | <100ms | 99.9% |
| Data Processing | `/fetch` | <5s | 95% |
| Configuration | `/config` | <500ms | 99% |
| Model Registry | `/models` | <200ms | 99.5% |
| Authentication | `/auth/health` | <100ms | 99.9% |

### Resource Usage Limits

| Resource | Limit | Monitoring |
|----------|-------|------------|
| CPU Usage | <80% | Continuous |
| Memory Usage | <512MB per service | Continuous |
| Active Connections | <100 per service | Continuous |

## 🔧 Configuration

### Service Configuration

The testing framework automatically detects services based on the following configuration:

```python
SERVICE_CONFIGS = {
    "model_registry": {
        "url": "http://localhost:8000",
        "endpoints": ["/health", "/models", "/providers"]
    },
    "feeds": {
        "url": "http://localhost:8005",
        "endpoints": ["/health", "/config", "/fetch"]
    },
    # ... other services
}
```

### Load Test Configuration

```python
LoadTestConfig(
    service_url="http://localhost:8005",
    endpoint="/fetch",
    method="POST",
    payload={"query": "test", "feed_type": "news"},
    concurrent_users=20,
    duration_seconds=60,
    ramp_up_seconds=10
)
```

### SLA Benchmarks

```python
SLABenchmark(
    service_name="feeds",
    endpoint="/fetch",
    max_response_time_ms=5000,
    min_success_rate_percent=95,
    min_requests_per_second=10,
    max_cpu_usage_percent=90,
    max_memory_usage_mb=1024
)
```

## 📊 Reports and Outputs

### Load Testing Reports

- **Performance Summary**: Response times, throughput, success rates
- **Error Analysis**: Failed requests and error patterns
- **Resource Usage**: CPU, memory, and network utilization
- **SLA Compliance**: Benchmark validation results

### UAT Reports

- **Scenario Results**: Pass/fail status for each test scenario
- **Business Validation**: End-to-end workflow verification
- **Performance Validation**: Response time and reliability checks
- **Error Handling**: Graceful degradation verification

### Performance Monitoring Reports

- **Real-time Metrics**: Live performance data
- **SLA Violations**: Compliance issues and alerts
- **Trend Analysis**: Performance over time
- **Resource Utilization**: System resource consumption

### Deployment Reports

- **Deployment Status**: Service deployment success/failure
- **Health Checks**: Service health validation
- **Rollback Events**: Deployment rollback activities
- **Monitoring Results**: Post-deployment monitoring

## 🚨 Troubleshooting

### Common Issues

1. **Service Not Responding**
   - Check if services are running on correct ports
   - Verify service health endpoints
   - Check network connectivity

2. **Load Test Failures**
   - Reduce concurrent users
   - Increase timeout values
   - Check system resources

3. **SLA Violations**
   - Review performance benchmarks
   - Check system resource usage
   - Optimize service configurations

4. **UAT Failures**
   - Verify test data and payloads
   - Check service dependencies
   - Review expected results

### Debug Mode

Enable verbose logging for detailed debugging:

```bash
python run_comprehensive_testing.py --verbose
```

### Manual Service Testing

Test individual services manually:

```python
import asyncio
from load_testing.load_test_framework import LoadTestFramework, LoadTestConfig

async def test_single_service():
    async with LoadTestFramework() as framework:
        config = LoadTestConfig(
            service_url="http://localhost:8005",
            endpoint="/health",
            concurrent_users=5,
            duration_seconds=30
        )
        result = await framework.run_load_test(config)
        print(framework.generate_report())

asyncio.run(test_single_service())
```

## 📝 Best Practices

### Load Testing

1. **Start Small**: Begin with light load and gradually increase
2. **Monitor Resources**: Watch CPU, memory, and network usage
3. **Test Realistic Scenarios**: Use actual data and workflows
4. **Document Results**: Save detailed reports for analysis

### UAT

1. **Business Focus**: Test actual business scenarios
2. **End-to-End**: Validate complete workflows
3. **Error Scenarios**: Test failure and recovery cases
4. **User Perspective**: Think from end-user viewpoint

### Performance Monitoring

1. **Continuous Monitoring**: Monitor in production
2. **Set Alerts**: Configure alerts for SLA violations
3. **Trend Analysis**: Track performance over time
4. **Capacity Planning**: Use data for scaling decisions

### Deployment

1. **Staged Deployment**: Deploy services in dependency order
2. **Health Checks**: Validate service health after deployment
3. **Rollback Plan**: Always have rollback procedures ready
4. **Monitoring**: Monitor deployment and post-deployment

## 🔄 Continuous Integration

### CI/CD Integration

The testing framework can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: Comprehensive Testing
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements_testing.txt
      - name: Start services
        run: docker-compose up -d
      - name: Run comprehensive testing
        run: python run_comprehensive_testing.py --phase=all
      - name: Upload test results
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: "*.json"
```

### Automated Testing

Set up automated testing schedules:

```bash
# Daily performance testing
0 2 * * * cd /path/to/sarvanom && python run_comprehensive_testing.py --phase=performance

# Weekly comprehensive testing
0 3 * * 0 cd /path/to/sarvanom && python run_comprehensive_testing.py --phase=all
```

## 📚 Additional Resources

- [Load Testing Best Practices](https://docs.example.com/load-testing)
- [Performance Monitoring Guide](https://docs.example.com/performance)
- [UAT Methodology](https://docs.example.com/uat)
- [Deployment Strategies](https://docs.example.com/deployment)

## 🤝 Contributing

To contribute to the testing framework:

1. Follow the existing code structure
2. Add comprehensive tests for new features
3. Update documentation
4. Ensure backward compatibility
5. Submit pull requests with detailed descriptions

## 📄 License

This testing framework is part of the SarvanOM project and follows the same license terms.
