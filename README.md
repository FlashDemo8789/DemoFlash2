# FLASH 2.0 - AI-Powered Startup Success Prediction Platform

![Status](https://img.shields.io/badge/Status-Production%20Ready-green)
![Version](https://img.shields.io/badge/Version-2.0.0-blue)
![ML Models](https://img.shields.io/badge/ML%20Models-11-purple)
![Accuracy](https://img.shields.io/badge/Accuracy-75%25-orange)

## 🚀 Overview
FLASH 2.0 is a revolutionary AI-powered platform that predicts startup success using advanced machine learning across 4 key pillars (CAMP):
- **C**apital: Financial health, burn rate, and efficiency metrics
- **A**dvantage: Technical moat, product differentiation, and scalability  
- **M**arket: TAM, growth dynamics, and competitive positioning
- **P**eople: Team quality, experience, and organizational strength

## ✨ Key Features
- **Revolutionary UI/UX**: 3D visualizations with Three.js and Framer Motion
- **11 ML Models**: Hierarchical ensemble with pillar-specific models
- **45 Core Features**: Carefully selected from 69 original metrics
- **Real-time Predictions**: < 100ms inference time
- **Explainable AI**: SHAP integration for transparency
- **Dark/Light Themes**: Beautiful, responsive design

## 🏃 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- npm or yarn

### 1. Start the API Server
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the FastAPI server
python api_server.py
```

### 2. Start the Frontend
```bash
# Navigate to frontend
cd flash-frontend

# Install dependencies
npm install

# Start development server
npm start
```

### 3. Access the Application
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🏗️ Architecture

### System Components
```
FLASH/
├── api_server.py                 # FastAPI inference server
├── train_model_v2_enhanced.py    # ML training pipeline
├── create_hybrid_dataset.py      # Dataset generation
├── models/                       # Trained ML models
│   ├── v2/                      # Base ensemble (5 models)
│   └── v2_enhanced/             # Pillar + meta models (7 models)
├── flash-frontend/              # React TypeScript app
│   ├── src/
│   │   ├── App.v2.tsx          # Main app with state management
│   │   ├── components/v2/       # Revolutionary UI components
│   │   └── styles/theme.v2.css  # Advanced theming
│   └── package.json
├── hybrid_startup_dataset.csv   # 100k company dataset
├── TECHNICAL_DOCUMENTATION.md   # Complete technical guide
└── PROJECT_STATUS_UPDATE.md     # Latest status report
```

### Technology Stack
- **Backend**: Python, FastAPI, Pydantic, NumPy, Pandas
- **ML**: CatBoost, scikit-learn, SHAP
- **Frontend**: React 18, TypeScript, Three.js, Framer Motion
- **Visualization**: 3D graphics, particle effects, animations

## 📊 Performance Metrics
- **Model Accuracy**: 72-75%
- **API Response**: < 100ms
- **Dataset Size**: 100,000 companies
- **Feature Count**: 45 (optimized from 69)
- **Success Rate**: 40.3% (balanced)

## 🎨 Revolutionary UI Features
- **3D Landing Page**: Animated sphere with particle effects
- **Interactive CAMP Cube**: Rotates based on active pillar
- **Smart Inputs**: AI-powered suggestions
- **Animated Results**: Success meter with gradients
- **Smooth Transitions**: Physics-based animations

## 🔧 API Endpoints

### Health Check
```bash
GET /health
```

### Prediction
```bash
POST /predict
Content-Type: application/json

{
  "total_funding_usd": 5000000,
  "funding_rounds_count": 2,
  "monthly_burn_usd": 150000,
  "annual_revenue_run_rate": 1200000,
  "team_size_total": 25,
  // ... 40 more features
}
```

### Response
```json
{
  "success_probability": 0.73,
  "confidence_score": 0.85,
  "risk_factors": ["High burn rate", "Limited runway"],
  "growth_indicators": ["Strong team", "Growing market"],
  "pillar_scores": {
    "capital": 0.68,
    "advantage": 0.81,
    "market": 0.75,
    "people": 0.88
  }
}
```

## 🧠 ML Model Architecture
- **Base Models**: 5 CatBoost models (ensemble)
- **Pillar Models**: 4 specialized models (CAMP)
- **Meta Model**: Combines pillar predictions
- **Direct Model**: Baseline comparison
- **Feature Engineering**: Automatic calculations for derived metrics

## 📈 Recent Updates (v2.0.0)
✅ Revolutionary UI/UX with 3D visualizations  
✅ Fixed CAMP score calculations  
✅ Fixed burn multiple formula (Net Burn / New ARR)  
✅ Fixed runway calculations (capped at 60 months)  
✅ Cleaned up 956MB of legacy files  
✅ Created comprehensive documentation  
✅ Achieved 75% prediction accuracy  

## 🚀 Future Roadmap
- [ ] Cloud deployment (AWS/GCP)
- [ ] Authentication system
- [ ] PDF report generation
- [ ] Mobile responsive design
- [ ] DNA pattern analysis
- [ ] Time-series predictions
- [ ] API SDK development

## 📝 Documentation
- [Technical Documentation](./TECHNICAL_DOCUMENTATION.md)
- [Project Status Update](./PROJECT_STATUS_UPDATE.md)
- [API Documentation](http://localhost:8000/docs)

## 🤝 Contributing
We welcome contributions! Please see our contributing guidelines (coming soon).

## 📄 License
Proprietary - All Rights Reserved

## 👥 Team
Built with ❤️ by the FLASH team using CatBoost, FastAPI, React, and Three.js.

---
**Status**: ✅ Production Ready | **Version**: 2.0.0 | **Last Updated**: May 25, 2025