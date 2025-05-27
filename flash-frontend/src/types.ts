// Type definitions for FLASH 2.0

export interface StartupData {
  // Capital metrics
  funding_stage: string;
  total_capital_raised_usd: number;
  cash_on_hand_usd: number;
  monthly_burn_usd: number;
  runway_months?: number;
  annual_revenue_run_rate: number;
  revenue_growth_rate_percent: number;
  gross_margin_percent: number;
  burn_multiple?: number;
  ltv_cac_ratio: number;
  investor_tier_primary: string;
  has_debt: boolean;
  
  // Advantage metrics
  patent_count: number;
  network_effects_present: boolean;
  has_data_moat: boolean;
  regulatory_advantage_present: boolean;
  tech_differentiation_score: number;
  switching_cost_score: number;
  brand_strength_score: number;
  scalability_score: number;
  product_stage: string;
  product_retention_30d: number;
  product_retention_90d: number;
  
  // Market metrics
  sector: string;
  tam_size_usd: number;
  sam_size_usd: number;
  som_size_usd: number;
  market_growth_rate_percent: number;
  customer_count: number;
  customer_concentration_percent: number;
  user_growth_rate_percent: number;
  net_dollar_retention_percent: number;
  competition_intensity: number;
  competitors_named_count: number;
  dau_mau_ratio: number;
  
  // People metrics
  founders_count: number;
  team_size_full_time: number;
  years_experience_avg: number;
  domain_expertise_years_avg: number;
  prior_startup_experience_count: number;
  prior_successful_exits_count: number;
  board_advisor_experience_score: number;
  advisors_count: number;
  team_diversity_percent: number;
  key_person_dependency: boolean;
  
  // Additional fields for frontend
  team_cohesion_score?: number;
  hiring_velocity_score?: number;
  diversity_score?: number;
  technical_expertise_score?: number;
}

export interface PredictionResult {
  success_probability: number;
  confidence_interval: {
    lower: number;
    upper: number;
  };
  risk_level: string;
  key_insights: string[];
  pillar_scores: {
    capital: number;
    advantage: number;
    market: number;
    people: number;
  };
  recommendation: string;
  timestamp: string;
  // New comprehensive evaluation fields
  verdict: 'PASS' | 'FAIL' | 'CONDITIONAL PASS';
  strength: 'STRONG' | 'MODERATE' | 'WEAK' | 'CRITICAL';
  weighted_score: number;
  critical_failures: string[];
  below_threshold: string[];
  stage_thresholds: {
    capital: number;
    advantage: number;
    market: number;
    people: number;
  };
}

export type Pillar = 'capital' | 'advantage' | 'market' | 'people';

export const PILLAR_NAMES: Record<Pillar, string> = {
  capital: 'Capital',
  advantage: 'Advantage',
  market: 'Market',
  people: 'People'
};

export const PILLAR_DESCRIPTIONS: Record<Pillar, string> = {
  capital: 'Financial health, funding, and burn efficiency',
  advantage: 'Competitive moat, IP, and differentiation',
  market: 'TAM, growth rate, and market dynamics',
  people: 'Team composition, experience, and leadership'
};