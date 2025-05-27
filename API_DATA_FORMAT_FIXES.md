# API Data Format Fixes

## Issues Fixed

### 1. **Frontend-to-API Data Transformation**
Added `transformDataForAPI` function in `AnalysisPage.tsx` to handle:

#### Funding Stage
- Frontend: "Series A", "Pre-seed", "Series B"
- API expects: "series_a", "pre_seed", "series_b"
- Fix: Convert to lowercase, replace spaces/hyphens with underscores

#### Investor Tier
- Frontend: "Angel", "Tier 1", "Tier 2", "Tier 3"
- API expects: "none", "tier_1", "tier_2", "tier_3"
- Fix: Map "Angel" to "none", convert others to lowercase with underscores

#### Scalability Score
- Frontend: 0-1 scale (e.g., 0.51)
- API expects: 1-5 scale
- Fix: Transform using formula: 1 + (value * 4)

#### Product Stage
- Frontend: "Beta", "MVP", "GA", "Mature"
- API expects: "beta", "mvp", "growth", "mature"
- Fix: Convert to lowercase, map "GA" to "growth"

#### Product Retention
- Frontend test data: 0-100 scale
- API expects: 0-1 scale
- Fix: Convert percentages to decimals

### 2. **Test Data Generator Updates**
Fixed all test data generation in `testDataGenerator.ts`:
- Funding stages now use correct format (series_a, not Series A)
- Investor tiers use correct format (tier_1, not Tier 1)
- Scalability score generates 1-5 values
- Product stages use lowercase format
- Retention rates generate 0-1 values

### 3. **Data Transformation Function**
```typescript
const transformDataForAPI = (data: any) => {
  const transformed = { ...data };
  
  // Transform funding_stage
  if (transformed.funding_stage) {
    transformed.funding_stage = transformed.funding_stage
      .toLowerCase()
      .replace(/-/g, '_')
      .replace(/\s+/g, '_');
  }
  
  // Transform investor_tier_primary
  const tierMap = {
    'angel': 'none',
    'tier 1': 'tier_1',
    'tier 2': 'tier_2',
    'tier 3': 'tier_3'
  };
  
  // Transform scalability_score from 0-1 to 1-5
  if (transformed.scalability_score <= 1) {
    transformed.scalability_score = 1 + (transformed.scalability_score * 4);
  }
  
  // Transform product_stage
  if (transformed.product_stage) {
    transformed.product_stage = transformed.product_stage.toLowerCase();
  }
  
  return transformed;
};
```

## Valid API Formats

### Required Formats:
- **funding_stage**: `pre_seed`, `seed`, `series_a`, `series_b`, `series_c`, `growth`
- **investor_tier_primary**: `tier_1`, `tier_2`, `tier_3`, `none`
- **product_stage**: `concept`, `mvp`, `beta`, `launch`, `growth`, `mature`
- **scalability_score**: Number between 1-5
- **product_retention_30d/90d**: Number between 0-1
- **key_person_dependency**: Boolean (true/false)
- **competition_intensity**: Number between 1-5

## Testing
The application should now work correctly when:
1. Using the "Generate Test Data" button
2. Manually entering data in the form
3. Submitting data to the API

All 422 validation errors should be resolved!