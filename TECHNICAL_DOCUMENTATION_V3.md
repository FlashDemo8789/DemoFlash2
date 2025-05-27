# FLASH Platform - Technical Documentation v3

## Overview
FLASH (Fast Learning and Assessment of Startup Health) is an AI-powered startup assessment platform that evaluates startups across four key dimensions (CAMP: Capital, Advantage, Market, People) using 11 specialized machine learning models with stage-based evaluation criteria.

## Major Updates in v3

### Complete UI/UX Redesign
- Removed all gamification elements
- Implemented Apple-inspired minimal design philosophy
- Professional interface suitable for VCs and founders
- Clean typography-first approach
- CAMP structure prominently displayed

### Enhanced Evaluation System
- Stage-based weights and thresholds
- Critical failure detection
- Risk-adjusted scoring
- Comprehensive verdict system (PASS/CONDITIONAL PASS/FAIL)
- Real-time model calculations (not hardcoded)

## Architecture

### Backend (FastAPI + Python)
- **Framework**: FastAPI with Uvicorn server
- **ML Models**: 11 CatBoost models
  - 5 Base ensemble models (conservative, aggressive, balanced, deep, direct)
  - 2 Meta models (logistic, CatBoost)
  - 4 Pillar-specific models (capital, advantage, market, people)
- **Validation**: Pydantic v2 for request/response validation
- **Port**: 8000
- **CORS**: Enabled for frontend integration

### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **State Management**: React hooks
- **Animation**: Framer Motion
- **Visualization**: Canvas-based constellation analysis
- **Styling**: CSS modules with minimal design system
- **Port**: 3000

## Data Architecture

### Input Data (45 Metrics)

#### Capital Pillar (10 metrics)
```typescript
funding_stage: string                    // Pre-seed, Seed, Series A/B/C
total_capital_raised_usd: number         // Total funding raised
cash_on_hand_usd: number                 // Current cash reserves
monthly_burn_usd: number                 // Monthly burn rate
annual_revenue_run_rate: number          // ARR
revenue_growth_rate_percent: number      // YoY growth %
gross_margin_percent: number             // Gross margin %
ltv_cac_ratio: number                    // LTV/CAC ratio
investor_tier_primary: string            // Tier 1/2/3/Angel
has_debt: boolean                        // Debt financing flag
```

#### Advantage Pillar (11 metrics)
```typescript
patent_count: number                     // Number of patents
network_effects_present: boolean         // Network effects flag
has_data_moat: boolean                   // Data moat flag
regulatory_advantage_present: boolean    // Regulatory advantage
tech_differentiation_score: number       // 1-5 scale
switching_cost_score: number             // 1-5 scale
brand_strength_score: number             // 1-5 scale
scalability_score: number                // 0-100% (converted to 0-1)
product_stage: string                    // MVP/Beta/GA/Mature
product_retention_30d: number            // 0-100% (converted to 0-1)
product_retention_90d: number            // 0-100% (converted to 0-1)
```

#### Market Pillar (12 metrics)
```typescript
sector: string                           // Industry sector
tam_size_usd: number                     // Total addressable market
sam_size_usd: number                     // Serviceable addressable market
som_size_usd: number                     // Serviceable obtainable market
market_growth_rate_percent: number       // Market CAGR %
customer_count: number                   // Number of customers
customer_concentration_percent: number   // Customer concentration %
user_growth_rate_percent: number         // User growth %
net_dollar_retention_percent: number     // NDR %
competition_intensity: number            // 1-5 scale
competitors_named_count: number          // Number of competitors
dau_mau_ratio: number                    // Daily/Monthly active users
```

#### People Pillar (10 metrics)
```typescript
founders_count: number                   // Number of founders
team_size_full_time: number              // Full-time employees
years_experience_avg: number             // Average years experience
domain_expertise_years_avg: number       // Domain expertise years
prior_startup_experience_count: number   // Prior startups
prior_successful_exits_count: number     // Successful exits
board_advisor_experience_score: number   // 1-5 scale
advisors_count: number                   // Number of advisors
team_diversity_percent: number           // Diversity percentage
key_person_dependency: boolean           // Key person risk
```

#### Calculated Fields
```typescript
runway_months: number                    // cash_on_hand / monthly_burn (max 60)
burn_multiple: number                    // Calculated server-side
```

## Enhanced Evaluation Algorithm

### Stage-Based Weights
```python
STAGE_WEIGHTS = {
    "Pre-seed": {"capital": 0.15, "advantage": 0.30, "market": 0.20, "people": 0.35},
    "Seed":     {"capital": 0.20, "advantage": 0.30, "market": 0.25, "people": 0.25},
    "Series A": {"capital": 0.25, "advantage": 0.25, "market": 0.30, "people": 0.20},
    "Series B": {"capital": 0.25, "advantage": 0.25, "market": 0.30, "people": 0.20},
    "Series C": {"capital": 0.30, "advantage": 0.20, "market": 0.30, "people": 0.20}
}
```

### Stage-Based Thresholds
```python
STAGE_THRESHOLDS = {
    "Pre-seed": {"capital": 0.30, "advantage": 0.40, "market": 0.30, "people": 0.50},
    "Seed":     {"capital": 0.35, "advantage": 0.45, "market": 0.40, "people": 0.50},
    "Series A": {"capital": 0.45, "advantage": 0.50, "market": 0.50, "people": 0.45},
    "Series B": {"capital": 0.50, "advantage": 0.55, "market": 0.55, "people": 0.50},
    "Series C": {"capital": 0.55, "advantage": 0.60, "market": 0.60, "people": 0.55}
}
```

### Critical Failure Conditions
```python
CRITICAL_FAILURES = {
    "runway_months < 3": "Less than 3 months runway - immediate funding required",
    "burn_multiple > 5": "Burning >5x revenue - unsustainable burn rate",
    "customer_concentration > 80%": "Over 80% customer concentration - extreme dependency",
    "churn_rate > 20%": "Monthly churn >20% - severe retention crisis",
    "single_founder + key_person_risk": "Single founder with high key person dependency"
}
```

### Risk Adjustments
```python
# Negative adjustments
- High customer concentration (>50%): -0.1
- Regulatory uncertainty (score >4): -0.15
- No network effects: -0.05
- Low switching costs (<3): -0.05
- High debt ratio (>2): -0.1
- Non-tier investor: -0.05

# Positive adjustments
- Tier 1 investors: +0.1
- Prior successful exits: +0.1
- Strong network effects: +0.1
- High NDR (>130%): +0.1
- Many patents (>5): +0.05
```

### Verdict Determination
```python
if critical_failures:
    verdict = "FAIL"
    strength = "CRITICAL"
elif all_pillars_meet_thresholds and weighted_score >= 0.6:
    verdict = "PASS"
    strength = "STRONG"
elif pillars_below_threshold <= 1 and weighted_score >= 0.55:
    verdict = "CONDITIONAL PASS"
    strength = "MODERATE"
elif weighted_score >= 0.5 and pillars_below_threshold <= 2:
    verdict = "CONDITIONAL PASS"
    strength = "WEAK"
else:
    verdict = "FAIL"
    strength = "WEAK"
```

## UI/UX Design System

### Design Philosophy
- **Minimalism**: Apple-inspired clean interfaces
- **Typography First**: Clear hierarchy using size and weight
- **No Gamification**: Professional context for serious decisions
- **Purposeful Motion**: Animations serve function, not decoration

### Color Palette
```css
/* Light Mode */
--color-primary: #111827;        /* Near black */
--color-secondary: #6b7280;      /* Gray 500 */
--color-background: #ffffff;     /* White */
--color-surface: #f9fafb;        /* Gray 50 */
--color-border: #e5e7eb;         /* Gray 200 */
--color-success: #10b981;        /* Green 500 */
--color-warning: #fbbf24;        /* Yellow 400 */
--color-error: #ef4444;          /* Red 500 */
--color-accent: #3b82f6;         /* Blue 500 */
```

### Component Architecture

#### 1. Landing Page (AppV3)
```tsx
- Clean CAMP grid with letter icons
- Minimal hero with gradient logo
- Single CTA button
- Professional disclaimer
```

#### 2. Data Collection (DataCollectionCAMP)
```tsx
- CAMP navigation pills with progress
- 2-column form grid
- Real-time validation
- Test data buttons (🎲, ⬆, ⬇)
- Stage-appropriate field organization
```

#### 3. Analysis Visualization (ConstellationAnalysis)
```tsx
- Canvas-based constellation pattern
- Stars representing startup (center) and pillars
- Dynamic connections forming during analysis
- Data flow particles
- Phase indicators
```

#### 4. Results Display (MinimalResults)
```tsx
- Hero metric (success probability %)
- Verdict badge (PASS/CONDITIONAL/FAIL)
- Weighted score display
- Pillar scores with thresholds
- Critical failures highlighted
- Clean insights without emojis
- Export/Share actions
```

## API Specification

### Endpoints

#### Health Check
```http
GET /health
Response: {
    "status": "healthy",
    "models_loaded": 11,
    "pillar_models_loaded": 4,
    "version": "2.0.0",
    "timestamp": "2025-05-25T11:38:50.899490"
}
```

#### Prediction
```http
POST /predict
Content-Type: application/json

Request Body: {
    // All 45 metrics as defined above
}

Response: {
    "success_probability": 0.73,
    "confidence_interval": {
        "lower": 0.68,
        "upper": 0.78
    },
    "risk_level": "Low Risk",
    "key_insights": [
        "Strong capital efficiency",
        "World-class team with proven experience",
        "Market challenges - improve PMF and retention"
    ],
    "pillar_scores": {
        "capital": 0.82,
        "advantage": 0.71,
        "market": 0.64,
        "people": 0.89
    },
    "recommendation": "✅ Solid foundation with clear growth path...",
    "timestamp": "2025-05-25T11:38:50.899490",
    "verdict": "PASS",
    "strength": "STRONG",
    "weighted_score": 0.745,
    "critical_failures": [],
    "below_threshold": ["market"],
    "stage_thresholds": {
        "capital": 0.45,
        "advantage": 0.50,
        "market": 0.50,
        "people": 0.45
    }
}
```

### Data Transformations

#### Frontend to API
1. **Percentage to Decimal Conversions**:
   - `product_retention_30d`: 60% → 0.6
   - `product_retention_90d`: 40% → 0.4
   - `scalability_score`: 70% → 0.7

2. **Type Conversions**:
   - All numeric fields: string → float
   - All boolean fields: any → boolean
   - Select fields: maintain string values

3. **Required Defaults**:
   ```javascript
   {
       revenue_growth_rate_percent: 0,
       ltv_cac_ratio: 0,
       patent_count: 0,
       user_growth_rate_percent: 0,
       customer_concentration_percent: 20,
       team_diversity_percent: 40,
       advisors_count: 0
   }
   ```

## Test Data Generator

### Startup Profiles
```javascript
const profiles = [
    'High Growth SaaS',      // Series A/B, high revenue growth
    'Early Stage Fintech',   // Pre-seed/Seed, limited metrics
    'Struggling E-commerce', // Poor retention, high burn
    'Mature Enterprise',     // Series B/C, stable metrics
    'Moonshot DeepTech',     // High potential, pre-revenue
    'Bootstrap Success',     // Profitable, no external funding
    'VC Darling',           // Tier 1 investors, hypergrowth
    'Pivot Candidate'       // Declining metrics, needs change
];
```

### Realistic Correlations
- TAM/SAM/SOM maintain proper relationships
- 90-day retention = 30-day retention × 0.5-0.9
- Funding amounts match stage
- Team size correlates with funding
- Revenue correlates with team size

### Test Scenarios
- **🎲 Random**: Generates data from random profile
- **⬆ Best Case**: All metrics optimized for success
- **⬇ Worst Case**: All metrics showing struggles

## Performance Metrics

### Backend Performance
- Model loading: ~2-3 seconds on startup
- Prediction latency: <100ms average
- API response time: <200ms (including network)
- Memory usage: ~500MB with models loaded

### Frontend Performance
- Initial bundle: ~500KB minified
- Time to interactive: <2 seconds
- Analysis animation: 10 seconds
- Smooth 60fps animations

## Security Considerations

### Input Validation
- All fields validated with Pydantic
- Type checking and range validation
- SQL injection prevention
- XSS protection in frontend

### API Security
- CORS configured for production domains
- Rate limiting recommended (not implemented)
- Authentication planned (JWT)
- No sensitive data in logs

### Data Privacy
- No PII storage
- All data processed in-memory
- No analytics tracking
- Secure model storage

## Deployment Guide

### Backend Deployment
```bash
# Clone repository
git clone [repository-url]
cd FLASH

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Start API server
python3 api_server.py
# API runs on http://localhost:8000
```

### Frontend Deployment
```bash
# Navigate to frontend
cd flash-frontend

# Install dependencies
npm install

# Development server
npm start
# Runs on http://localhost:3000

# Production build
npm run build
# Creates optimized build in build/

# Serve production build
npm install -g serve
serve -s build
```

### Environment Variables
```bash
# Frontend (.env)
REACT_APP_API_URL=http://localhost:8000

# Backend (optional)
MODEL_PATH=./models/v2
LOG_LEVEL=INFO
```

## Known Issues & Limitations

### Current Issues
1. Three.js deprecation warnings (non-blocking)
2. ESLint warnings for unused imports
3. Pydantic v2 migration warnings
4. Missing comprehensive test suite
5. No error boundaries in some components

### Limitations
1. Single-company predictions only (no batch)
2. English language only
3. No data persistence
4. No user accounts
5. Limited mobile responsiveness

## Future Roadmap

### Phase 1: Infrastructure
- [ ] JWT authentication
- [ ] User accounts and saved analyses
- [ ] Batch prediction API
- [ ] PostgreSQL integration
- [ ] Redis caching

### Phase 2: Features
- [ ] PDF report generation
- [ ] Comparison tools
- [ ] Historical tracking
- [ ] Team collaboration
- [ ] API rate limiting

### Phase 3: ML Enhancements
- [ ] Real-time model updates
- [ ] Industry-specific models
- [ ] Time-series predictions
- [ ] Explainable AI dashboard
- [ ] Model A/B testing

### Phase 4: Platform
- [ ] Mobile app
- [ ] API SDK (Python/JS)
- [ ] Webhook integrations
- [ ] Third-party data sources
- [ ] White-label options

## Version History

### v3.0 (Current) - May 2025
- Complete UI redesign (removed gamification)
- Stage-based evaluation system
- Critical failure detection
- Professional CAMP-based interface
- Test data generator
- Bug fixes and performance improvements

### v2.0 - April 2025
- Enhanced scoring algorithms
- 11-model ensemble
- Pillar-specific insights
- 3D visualizations
- Dark mode support

### v1.0 - March 2025
- Initial release
- Basic ML models
- Simple web interface
- 45 feature collection

## Development Best Practices

### Code Style
- TypeScript for type safety
- ESLint + Prettier for consistency
- Functional components with hooks
- Async/await for API calls

### Git Workflow
- Feature branches
- Descriptive commit messages
- PR reviews required
- Semantic versioning

### Testing Strategy
- Unit tests for utilities
- Integration tests for API
- E2E tests for critical paths
- Manual QA for UI/UX

## Support & Documentation

### Getting Help
- Check console for detailed error logs
- API documentation at `/docs`
- Frontend uses inline TypeScript docs
- Model interpretability via SHAP

### Contributing
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request
5. Wait for review

## Conclusion

FLASH v3 represents a significant evolution in startup assessment technology, combining sophisticated machine learning with professional, minimal design. The platform provides institutional-grade analysis while maintaining ease of use, making it suitable for VCs, accelerators, and startup founders alike.

Last Updated: May 25, 2025