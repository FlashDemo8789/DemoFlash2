# FLASH Platform - Technical Documentation v4

## Overview
FLASH (Fast Learning and Assessment of Startup Health) is an AI-powered startup assessment platform that evaluates startups across four key dimensions (CAMP: Capital, Advantage, Market, People) using 11 specialized machine learning models with stage-based evaluation criteria, enhanced security, and production-ready deployment.

## Major Updates in v4

### Security Enhancements
- **CORS Configuration**: Environment-based allowed origins
- **Rate Limiting**: 100 requests/hour per IP/API key (configurable)
- **Input Validation**: Enhanced Pydantic v2 constraints with regex patterns
- **Request Size Limits**: 1MB maximum request size
- **API Key Authentication**: Support for API key-based access
- **Security Headers**: XSS, CSRF, and clickjacking protection

### Testing Infrastructure
- **Comprehensive Test Suite**: pytest with 40+ test cases
- **Test Coverage**: API endpoints, validation, rate limiting, security
- **Fixtures**: Valid, invalid, and edge case test data
- **Async Support**: Tests for async endpoints
- **CI/CD Ready**: Test runner script with coverage reports

### Production Deployment
- **Docker Support**: Multi-stage Dockerfile for optimized images
- **Docker Compose**: Full stack deployment with nginx, Prometheus
- **Environment Configuration**: .env-based configuration management
- **SSL/TLS Ready**: nginx configuration for HTTPS
- **Health Checks**: Liveness and readiness probes
- **Monitoring**: Prometheus metrics integration

### ML Model Improvements
- **Stage-Based Hierarchical Models**: 5-10% accuracy improvement
- **Stage-Specific Features**: Custom features per funding stage
- **Dynamic Thresholds**: Different success criteria per stage
- **Meta-Model Ensemble**: Combines stage and base predictions
- **Feature Importance**: Stage-specific feature analysis

### Frontend Improvements
- **Three.js Optimization**: Fixed deprecation warnings
- **Performance**: Source map generation disabled for production
- **Canvas Configuration**: Proper camera and GL settings
- **Warning Suppression**: Development console cleanup

## Architecture

### Backend (FastAPI + Python)
- **Framework**: FastAPI 0.104.1 with Uvicorn server
- **ML Models**: 
  - 11 Base CatBoost models
  - 6 Stage-specific hierarchical models
  - Meta-model ensemble combining predictions
- **Security**: Rate limiting, CORS, input validation
- **Configuration**: Environment-based settings
- **Testing**: pytest with async support
- **Deployment**: Docker + Gunicorn with 4 workers

### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **3D Graphics**: Three.js with @react-three/fiber
- **State Management**: React hooks
- **Animation**: Framer Motion
- **Visualization**: Canvas-based constellation analysis
- **Styling**: CSS modules with minimal design system
- **Build**: Optimized production builds with nginx

## Security Implementation

### API Security
```python
# Rate limiting configuration
RATE_LIMIT_REQUESTS = 100  # requests
RATE_LIMIT_WINDOW = 3600   # seconds (1 hour)

# CORS configuration
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://app.flash-platform.com"
]

# Request validation
MAX_REQUEST_SIZE = 1048576  # 1MB
API_KEY_HEADER = "X-API-Key"
```

### Input Validation
```python
# Enhanced Pydantic models with constraints
funding_stage: str = Field(..., regex="^(pre_seed|seed|series_a|series_b|series_c|growth)$")
total_capital_raised_usd: confloat(ge=0, le=1e10)
team_diversity_percent: confloat(ge=0, le=100)
```

## Stage-Based Hierarchical Models

### Stage-Specific Weights
```python
stage_feature_weights = {
    'pre_seed': {
        'people': 0.40,     # Team is crucial early
        'advantage': 0.30,  # Product vision matters
        'market': 0.20,     # Market validation
        'capital': 0.10     # Less critical early
    },
    'series_a': {
        'market': 0.30,     # Growth metrics matter
        'advantage': 0.25,
        'capital': 0.25,    # Efficiency crucial
        'people': 0.20
    },
    'growth': {
        'capital': 0.45,    # Financial metrics dominate
        'market': 0.35,
        'advantage': 0.15,
        'people': 0.05
    }
}
```

### Stage-Specific Thresholds
```python
stage_thresholds = {
    'pre_seed': {
        'min_team_size': 2,
        'min_experience_years': 3,
        'min_retention_30d': 0.3,
        'max_burn_multiple': 10,
        'min_runway_months': 6
    },
    'series_a': {
        'min_team_size': 15,
        'min_experience_years': 7,
        'min_retention_30d': 0.5,
        'max_burn_multiple': 5,
        'min_runway_months': 18,
        'min_revenue': 1000000,
        'min_growth_rate': 0.5
    }
}
```

## API Endpoints

### Enhanced Endpoints
```
POST /predict
- Rate limited: 100 requests/hour
- Input validation with regex patterns
- Stage-based model predictions
- Response time: <500ms

POST /explain  
- Rate limited: 50 requests/hour
- SHAP-based explanations
- Feature importance visualization

GET /health
- Health check with model status
- No rate limiting
- Prometheus metrics compatible
```

## Testing

### Test Categories
1. **Unit Tests**: Model predictions, validation logic
2. **Integration Tests**: API endpoints, database operations
3. **Security Tests**: Rate limiting, CORS, authentication
4. **Performance Tests**: Response times, load handling

### Running Tests
```bash
# Run all tests with coverage
python run_tests.py

# Run specific test category
pytest tests/test_api.py -v

# Generate coverage report
pytest --cov=api_server --cov-report=html
```

## Deployment

### Docker Deployment
```bash
# Build and deploy
./deploy.sh deploy

# View status
./deploy.sh status

# View logs
./deploy.sh logs api
```

### Environment Variables
```env
# Security
ENVIRONMENT=production
SECRET_KEY=your-secret-key
ALLOWED_ORIGINS=https://app.flash-platform.com
API_KEYS=key1,key2,key3

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Model Configuration
MODEL_BASE_PATH=models/v2_enhanced
STAGE_MODEL_PATH=models/stage_hierarchical
```

### Production Architecture
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   nginx     │────▶│  Frontend   │────▶│     API     │
│  (SSL/TLS)  │     │  (React)    │     │  (FastAPI)  │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                        ┌──────┴──────┐
                                        │   ML Models  │
                                        │  (11 + 6)   │
                                        └─────────────┘
```

## Performance Optimizations

### API Performance
- Model preloading on startup
- Connection pooling for concurrent requests
- Response caching for repeated predictions
- Async request handling

### Frontend Performance
- Code splitting and lazy loading
- Optimized Three.js rendering
- Minimal re-renders with React.memo
- Production builds with minification

## Monitoring

### Metrics Collection
- Request latency histograms
- Model prediction times
- Error rates by endpoint
- Rate limit violations

### Prometheus Configuration
```yaml
scrape_configs:
  - job_name: 'flash-api'
    static_configs:
      - targets: ['api:9090']
    metrics_path: '/metrics'
```

## Known Issues

### Resolved
- ✅ Three.js deprecation warnings (fixed with proper Canvas configuration)
- ✅ Missing 45 metrics in frontend (all fields added)
- ✅ API 422 validation errors (percentage conversions fixed)
- ✅ Navigation flow issues (auto-navigation implemented)

### Pending
- ⚠️ Pydantic v2 migration warnings (non-blocking)
- ⚠️ ESLint warnings for unused imports (cosmetic)
- ⚠️ Model loading time on cold start (~5 seconds)

## Future Roadmap

### Next Sprint (2 weeks)
1. **Model Monitoring**: Drift detection and A/B testing
2. **Batch Predictions**: Process multiple startups
3. **User Authentication**: JWT-based auth system
4. **CI/CD Pipeline**: GitHub Actions workflow

### Q2 2025
1. **Temporal Models**: Time-based predictions
2. **Industry-Specific Models**: Vertical optimization
3. **DNA Pattern Analysis**: Growth pattern recognition
4. **Mobile App**: React Native implementation

## Support

For issues or questions:
- GitHub Issues: https://github.com/anthropics/flash-platform/issues
- Documentation: https://docs.flash-platform.com
- API Status: https://status.flash-platform.com

---
**Last Updated**: May 25, 2025  
**Version**: 4.0.0  
**Contributors**: Claude, SF