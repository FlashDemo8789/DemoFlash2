# FLASH Platform Technical Documentation

## Overview
FLASH is an AI-powered startup success prediction platform that leverages machine learning to evaluate startups across four key pillars: Capital, Advantage, Market, and People (CAMP). The platform provides actionable insights to investors, founders, and stakeholders through a revolutionary web interface and robust API.

## Architecture

### System Components
1. **Data Generation Pipeline** - Synthetic dataset creation with realistic patterns
2. **ML Training Pipeline** - Hierarchical model architecture with CatBoost
3. **Inference API** - FastAPI server with real-time predictions
4. **Frontend Application** - React TypeScript with 3D visualizations
5. **Model Storage** - Versioned model artifacts with enhanced variants

### Technology Stack
- **Backend**: Python 3.9+, FastAPI, Pydantic, NumPy, Pandas
- **ML Framework**: CatBoost, scikit-learn, SHAP
- **Frontend**: React 18, TypeScript, Three.js, Framer Motion
- **Styling**: CSS Variables, Dark/Light themes
- **API**: RESTful design with JSON payloads

## Data Architecture

### Feature Engineering (45 Core Features)
The platform uses 45 carefully selected features organized by CAMP pillars:

#### Capital Pillar (11 features)
- `total_funding_usd` - Total funding raised
- `funding_rounds_count` - Number of funding rounds
- `last_funding_amount_usd` - Most recent funding amount
- `months_since_last_funding` - Time since last funding
- `founder_ownership_percentage` - Founder equity stake
- `monthly_burn_usd` - Monthly cash burn rate
- `runway_months` - Calculated runway (capped at 60)
- `annual_revenue_run_rate` - ARR
- `revenue_growth_rate` - YoY revenue growth
- `burn_multiple` - Net burn / New ARR (capped at 10)
- `cash_efficiency_score` - Revenue per dollar burned

#### Advantage Pillar (11 features)
- `tech_stack_complexity_score` - Technology sophistication
- `proprietary_tech_flag` - Proprietary technology indicator
- `ai_ml_capability_flag` - AI/ML capabilities
- `platform_scalability_score` - Scalability assessment
- `api_product_flag` - API-first product
- `time_to_market_months` - Speed to market
- `nps_score` - Net Promoter Score
- `monthly_active_users` - MAU
- `user_growth_rate` - User growth percentage
- `churn_rate` - Monthly churn
- `customer_acquisition_cost` - CAC

#### Market Pillar (11 features)
- `tam_size_usd` - Total Addressable Market
- `sam_percentage` - Serviceable Addressable Market %
- `market_growth_rate` - Market CAGR
- `competitive_intensity_score` - Competition level
- `market_timing_score` - Market readiness
- `regulatory_risk_score` - Regulatory challenges
- `customer_concentration_score` - Customer diversity
- `revenue_concentration_herfindahl` - Revenue concentration
- `gross_margin` - Gross profit margin
- `market_share_percentage` - Current market share
- `category_leader_flag` - Market leadership indicator

#### People Pillar (12 features)
- `founding_team_size` - Number of founders
- `team_size_total` - Total employees
- `technical_team_percentage` - % technical staff
- `founders_experience_score` - Combined founder experience
- `founders_previous_exits` - Successful exit count
- `team_diversity_score` - Diversity metrics
- `advisory_board_size` - Number of advisors
- `advisory_board_quality_score` - Advisor caliber
- `employee_growth_rate` - Hiring velocity
- `glassdoor_rating` - Employee satisfaction
- `key_hire_score` - Quality of recent hires
- `culture_score` - Company culture assessment

### Dataset Generation
- **Hybrid Dataset Generator** (`create_hybrid_dataset.py`)
  - 100,000 synthetic companies with realistic distributions
  - Sector-based metric generation with correlations
  - 40.3% success rate with balanced outcomes
  - Stage-appropriate financial metrics

## Machine Learning Pipeline

### Model Architecture
Hierarchical ensemble with 11 total models:

#### Version 2 Models (`models/v2/`)
1. `model_v2_catboost_0.pkl` through `model_v2_catboost_4.pkl` - Base ensemble models
2. `scaler_v2.pkl` - StandardScaler for normalization

#### Version 2 Enhanced Models (`models/v2_enhanced/`)
1. `model_pillar_capital.pkl` - Capital pillar specialist
2. `model_pillar_advantage.pkl` - Advantage pillar specialist
3. `model_pillar_market.pkl` - Market pillar specialist
4. `model_pillar_people.pkl` - People pillar specialist
5. `model_meta.pkl` - Meta-model combining pillar predictions
6. `model_direct.pkl` - Direct prediction model
7. `scaler_enhanced.pkl` - Enhanced scaler

### Training Pipeline (`train_model_v2_enhanced.py`)
- Pillar-specific models trained on domain features
- Meta-model combines pillar predictions
- Direct model for baseline comparison
- Cross-validation with stratified sampling
- SHAP integration for explainability

### Model Performance
- Average accuracy: ~72-75%
- Balanced precision/recall
- Low false positive rate for investor confidence

## API Architecture

### FastAPI Server (`api_server.py`)
- **Endpoints**:
  - `GET /` - API documentation
  - `GET /health` - Health check with model status
  - `POST /predict` - Main prediction endpoint
  - `GET /features` - List required features

### Request/Response Schema
```python
class StartupDataInput(BaseModel):
    # 45 features with validation
    total_funding_usd: Optional[float] = Field(ge=0)
    # ... all other features
    
    # Calculated fields
    @validator('burn_multiple', pre=True, always=True)
    def calculate_burn_multiple(cls, v, values):
        # Proper burn multiple calculation
        # Burn Multiple = Net Burn / New ARR

class PredictionResponse(BaseModel):
    success_probability: float = Field(ge=0, le=1)
    confidence_score: float = Field(ge=0, le=1)
    risk_factors: List[str]
    growth_indicators: List[str]
    key_metrics: Dict[str, float]
    recommendations: List[str]
    pillar_scores: PillarScores
```

### API Features
- Automatic field calculation for derived metrics
- Comprehensive validation with Pydantic
- CORS enabled for frontend integration
- Detailed error messages
- Model versioning support

## Frontend Architecture

### Revolutionary UI/UX Design (v2)
Complete redesign with 3D visualizations and advanced animations:

#### Component Structure
```
src/
├── App.v2.tsx              # Main app with state management
├── components/v2/
│   ├── LandingPageV2.tsx   # 3D animated landing
│   ├── DataCollectionV2.tsx # Interactive CAMP cube
│   └── ResultsPageV2.tsx   # Animated results display
├── styles/
│   └── theme.v2.css        # Revolutionary theme system
└── types.ts                # TypeScript interfaces
```

#### Key Features
1. **3D Visualizations**
   - Animated sphere on landing page with distortion effects
   - Rotating CAMP cube during data collection
   - Particle effects and floating elements

2. **Motion Design**
   - Framer Motion for smooth transitions
   - Staggered animations for list items
   - Spring physics for interactive elements
   - Typewriter effects for insights

3. **Interactive Elements**
   - Smart input fields with AI suggestions
   - Visual sliders with real-time feedback
   - Progress rings and animated meters
   - Glassmorphism effects

4. **Theme System**
   - Dark mode by default
   - CSS variables for consistency
   - Gradient color schemes
   - Smooth theme transitions

### State Management
- React hooks for local state
- Four app states: landing, collection, analyzing, results
- Optimistic UI updates
- Error boundary implementation

## Data Flow

1. **User Journey**
   ```
   Landing Page → Data Collection → API Call → Analyzing State → Results
   ```

2. **API Integration**
   - Frontend collects 45 features through CAMP-organized forms
   - Validates and sends to FastAPI backend
   - Backend calculates derived metrics
   - ML models generate predictions
   - Results displayed with visualizations

3. **Real-time Calculations**
   - Burn multiple: `Net Burn / New ARR`
   - Runway: `Cash / Monthly Burn` (capped at 60)
   - Cash efficiency: `Revenue / Burn`

## Deployment Considerations

### Backend Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Run API server
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Deployment
```bash
# Install dependencies
cd flash-frontend
npm install

# Development
npm start

# Production build
npm run build
```

### Environment Variables
- `REACT_APP_API_URL` - API endpoint (default: http://localhost:8000)
- `MODEL_PATH` - Model directory path
- `LOG_LEVEL` - Logging verbosity

## Security Considerations

1. **API Security**
   - Input validation on all endpoints
   - Rate limiting recommendations
   - CORS configuration for production
   - No sensitive data in responses

2. **Data Privacy**
   - No PII storage
   - Synthetic data for development
   - Secure model storage
   - Audit logging capability

## Performance Optimizations

1. **Model Loading**
   - Models loaded once at startup
   - In-memory caching
   - Efficient numpy operations
   - Batch prediction support

2. **Frontend Performance**
   - Code splitting with React.lazy
   - Memoization for expensive calculations
   - Debounced API calls
   - Optimized 3D rendering

## Monitoring and Maintenance

### Health Checks
- API health endpoint with model status
- Version tracking for models
- Response time monitoring
- Error rate tracking

### Model Management
- Versioned model storage
- A/B testing framework ready
- Model drift detection planned
- Regular retraining pipeline

## Future Enhancements

1. **Technical Roadmap**
   - PDF report generation
   - Batch prediction API
   - WebSocket for real-time updates
   - Mobile responsive design
   - Multi-language support

2. **ML Improvements**
   - DNA sequence pattern analysis
   - Time-series predictions
   - Industry-specific models
   - Explainable AI dashboard

3. **Platform Features**
   - User authentication
   - Historical tracking
   - Comparison tools
   - API SDK development
   - Integration marketplace

## Testing Strategy

### Unit Tests
- Model prediction accuracy
- API endpoint validation
- Feature calculation logic
- Frontend component tests

### Integration Tests
- End-to-end user flows
- API contract testing
- Cross-browser compatibility
- Performance benchmarks

## Conclusion

FLASH represents a comprehensive AI-powered platform for startup evaluation, combining advanced machine learning with revolutionary user experience design. The modular architecture ensures scalability, while the hierarchical model approach provides both accuracy and explainability.

The platform is production-ready with:
- Robust API with comprehensive validation
- Revolutionary UI with 3D visualizations
- Scalable ML pipeline with 11 models
- Complete feature engineering
- Professional documentation

For questions or contributions, please refer to the project repository.