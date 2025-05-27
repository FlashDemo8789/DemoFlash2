# CLAUDE.md - AI Assistant Context

This file provides context and guidelines for AI assistants (like Claude) working on the FLASH platform.

## 🎯 Project Overview

FLASH is an AI-powered startup assessment platform that helps VCs make data-driven investment decisions. It uses advanced ML models to analyze startups across the CAMP framework (Capital, Advantage, Market, People).

## 🏗️ Project Structure

```
flash-frontend/               # React TypeScript frontend
├── src/
│   ├── components/v3/       # Latest component versions
│   ├── AppV3.tsx           # Main app component
│   └── index.tsx           # Entry point
└── build/                  # Production build

flash-backend-api/          # Python FastAPI backend
├── api_server.py          # Main API server
├── ml_models/             # Trained ML models
└── advanced_models.py     # Model implementations
```

## 🔧 Development Guidelines

### Code Style
- **TypeScript**: Use strict typing, avoid `any`
- **React**: Functional components with hooks
- **CSS**: CSS-in-JS or CSS modules, BEM naming
- **Python**: PEP 8 compliant, type hints preferred

### Component Guidelines
- Always use v3 components (latest version)
- Prefer WorldClassResults over EnhancedResults
- Use Framer Motion for animations
- Implement proper error boundaries

### API Guidelines
- Use /predict_advanced for full analysis
- Transform data before sending to API
- Handle errors gracefully
- Log important events

## 🚀 Common Commands

```bash
# Frontend
cd flash-frontend
npm install          # Install dependencies
npm start           # Start dev server (port 3000)
npm run build       # Build for production
npm run lint        # Run linter
npm run typecheck   # Check TypeScript

# Backend
cd flash-backend-api
pip install -r requirements.txt  # Install dependencies
python api_server.py            # Start API (port 8000)
python test_model.py           # Test ML models
```

## 📊 Key Features

### ML Models
1. **Stage-Based Model**: Evaluates based on funding stage
2. **DNA Pattern Analyzer**: Identifies growth patterns
3. **Temporal Predictor**: Forecasts future success
4. **Industry Models**: Sector-specific analysis

### Frontend Components
1. **WorldClassResults**: Premium results display
2. **FullAnalysisView**: Tabbed detailed analysis
3. **AnalysisOrb**: DNA helix loading animation
4. **DataCollectionCAMP**: Smart data collection

## 🎨 Design System

### Colors
- Primary: #007AFF
- Success: #00C851
- Warning: #FF8800
- Danger: #FF4444
- Background: #0A0A0C → #1A1A1F

### Fonts
- Primary: SF Pro Display
- Fallback: Inter, system fonts
- Weights: 400, 500, 600, 700, 800

### Effects
- Glassmorphism with backdrop-filter
- Smooth spring animations
- Gradient text and borders
- Multi-layer shadows

## 🐛 Known Issues

1. **Data Format**: Frontend sends "Series A", API expects "series_a"
2. **Memory Leak**: After 50+ analyses in single session
3. **Safari**: Gradient rendering issues
4. **TypeScript**: Some ESLint warnings remain

## 📝 Important Context

### Recent Changes
- Migrated from EnhancedResults to WorldClassResults
- Added DNA helix animation replacing circular orb
- Implemented /predict_advanced endpoint
- Fixed Pydantic v2 compatibility

### Data Transformations
```typescript
// Always transform data before API calls
const transformDataForAPI = (data) => {
  // funding_stage: "Series A" → "series_a"
  // investor_tier: "Angel" → "none"
  // scalability_score: 0-1 → 1-5
  // product_stage: "Beta" → "beta"
}
```

### Testing Approach
- No automated tests yet (planned)
- Manual testing required
- Check both standard and advanced APIs
- Test all screen sizes

## 🚦 Development Workflow

1. **Before Starting**
   - Check TODO_PENDING_WORK.md
   - Read recent commits
   - Ensure servers are running

2. **Making Changes**
   - Use v3 components only
   - Follow existing patterns
   - Test in both Chrome and Safari
   - Check mobile responsiveness

3. **Before Committing**
   - Run `npm run build`
   - Fix any TypeScript errors
   - Test the full user flow
   - Update documentation if needed

## 💡 Tips for AI Assistants

1. **Always Check First**
   - Current component versions (use v3)
   - Existing patterns in codebase
   - Data format requirements

2. **Common Pitfalls**
   - Don't use old component versions
   - Remember data transformations
   - Check for TypeScript errors
   - Test animations performance

3. **Best Practices**
   - Keep animations smooth (60fps)
   - Maintain dark theme consistency
   - Use proper TypeScript types
   - Handle loading and error states

4. **When Stuck**
   - Check TECHNICAL_DOCUMENTATION_V4.md
   - Look at similar components
   - Review recent git commits
   - Ask for clarification

## 🔗 Key Files Reference

- **Main App**: `src/AppV3.tsx`
- **Results Display**: `src/components/v3/WorldClassResults.tsx`
- **API Server**: `flash-backend-api/api_server.py`
- **ML Models**: `flash-backend-api/advanced_models.py`
- **Styles**: `src/components/v3/WorldClassResults.css`

## 📞 Communication Style

When providing updates or explanations:
- Be concise and clear
- Show relevant code snippets
- Explain the "why" behind changes
- Highlight potential impacts
- Suggest testing steps

---

*This file helps AI assistants understand the FLASH platform context and work more effectively on the codebase.*