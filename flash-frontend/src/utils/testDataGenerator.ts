// Test Data Generator for FLASH Platform
// Generates realistic random startup data for testing

import { StartupData } from '../types';

// Startup profiles with different characteristics
const startupProfiles = [
  { name: 'High Growth SaaS', category: 'high-growth' },
  { name: 'Early Stage Fintech', category: 'early-stage' },
  { name: 'Struggling E-commerce', category: 'struggling' },
  { name: 'Mature Enterprise', category: 'mature' },
  { name: 'Moonshot DeepTech', category: 'moonshot' },
  { name: 'Bootstrap Success', category: 'bootstrap' },
  { name: 'VC Darling', category: 'vc-backed' },
  { name: 'Pivot Candidate', category: 'pivot' }
];

// Helper functions
const randomBetween = (min: number, max: number): number => {
  return Math.floor(Math.random() * (max - min + 1)) + min;
};

const randomFloat = (min: number, max: number, decimals: number = 2): number => {
  const value = Math.random() * (max - min) + min;
  return parseFloat(value.toFixed(decimals));
};

const randomChoice = <T>(array: T[]): T => {
  return array[Math.floor(Math.random() * array.length)];
};

// Generate data based on profile
export const generateTestStartupData = (): Partial<StartupData> => {
  const profile = randomChoice(startupProfiles);
  const baseData: Partial<StartupData> = {};
  
  // Set stage-appropriate defaults
  switch (profile.category) {
    case 'high-growth':
      baseData.funding_stage = randomChoice(['series_a', 'series_b']);
      baseData.total_capital_raised_usd = randomBetween(10000000, 50000000);
      baseData.cash_on_hand_usd = randomBetween(5000000, 20000000);
      baseData.monthly_burn_usd = randomBetween(200000, 500000);
      baseData.annual_revenue_run_rate = randomBetween(5000000, 20000000);
      baseData.revenue_growth_rate_percent = randomBetween(100, 300);
      baseData.gross_margin_percent = randomBetween(70, 85);
      baseData.team_size_full_time = randomBetween(50, 150);
      baseData.runway_months = randomBetween(18, 36);
      baseData.burn_multiple = randomFloat(1, 3);
      break;
      
    case 'early-stage':
      baseData.funding_stage = randomChoice(['pre_seed', 'seed']);
      baseData.total_capital_raised_usd = randomBetween(100000, 2000000);
      baseData.cash_on_hand_usd = randomBetween(50000, 1000000);
      baseData.monthly_burn_usd = randomBetween(20000, 100000);
      baseData.annual_revenue_run_rate = randomBetween(0, 500000);
      baseData.revenue_growth_rate_percent = randomBetween(0, 100);
      baseData.gross_margin_percent = randomBetween(40, 70);
      baseData.team_size_full_time = randomBetween(3, 20);
      break;
      
    case 'struggling':
      baseData.funding_stage = randomChoice(['seed', 'series_a']);
      baseData.total_capital_raised_usd = randomBetween(1000000, 5000000);
      baseData.cash_on_hand_usd = randomBetween(100000, 500000);
      baseData.monthly_burn_usd = randomBetween(100000, 300000);
      baseData.annual_revenue_run_rate = randomBetween(100000, 1000000);
      baseData.revenue_growth_rate_percent = randomBetween(-20, 30);
      baseData.gross_margin_percent = randomBetween(20, 50);
      baseData.team_size_full_time = randomBetween(10, 30);
      break;
      
    case 'mature':
      baseData.funding_stage = randomChoice(['series_b', 'series_c']);
      baseData.total_capital_raised_usd = randomBetween(30000000, 100000000);
      baseData.cash_on_hand_usd = randomBetween(10000000, 40000000);
      baseData.monthly_burn_usd = randomBetween(500000, 1000000);
      baseData.annual_revenue_run_rate = randomBetween(20000000, 100000000);
      baseData.revenue_growth_rate_percent = randomBetween(50, 100);
      baseData.gross_margin_percent = randomBetween(60, 80);
      baseData.team_size_full_time = randomBetween(100, 500);
      break;
      
    default:
      // Random mix
      baseData.funding_stage = randomChoice(['Pre-seed', 'Seed', 'Series A', 'Series B']);
      baseData.total_capital_raised_usd = randomBetween(100000, 20000000);
      baseData.cash_on_hand_usd = randomBetween(50000, 10000000);
      baseData.monthly_burn_usd = randomBetween(20000, 500000);
      baseData.annual_revenue_run_rate = randomBetween(0, 10000000);
      baseData.revenue_growth_rate_percent = randomBetween(-10, 200);
      baseData.gross_margin_percent = randomBetween(30, 80);
      baseData.team_size_full_time = randomBetween(5, 100);
  }
  
  // Calculate TAM/SAM/SOM relationship
  const tam = randomBetween(1000000000, 100000000000);
  const sam = tam * randomFloat(0.05, 0.3);
  const som = sam * randomFloat(0.01, 0.1);
  
  // Calculate retention relationship
  const retention30d = randomFloat(0.20, 0.95);
  const retention90d = retention30d * randomFloat(0.5, 0.9);
  
  // Fill in remaining fields with correlated values
  return {
    ...baseData,
    
    // Capital fields
    ltv_cac_ratio: randomFloat(0.5, 5),
    investor_tier_primary: randomChoice(['tier_1', 'tier_2', 'tier_3', 'none']),
    has_debt: Math.random() > 0.7,
    
    // Advantage fields
    patent_count: randomBetween(0, 10),
    network_effects_present: Math.random() > 0.5,
    has_data_moat: Math.random() > 0.6,
    regulatory_advantage_present: Math.random() > 0.8,
    tech_differentiation_score: randomBetween(1, 5),
    switching_cost_score: randomBetween(1, 5),
    brand_strength_score: randomBetween(1, 5),
    scalability_score: randomBetween(1, 5),
    product_stage: randomChoice(['mvp', 'beta', 'growth', 'mature']),
    product_retention_30d: retention30d,
    product_retention_90d: retention90d,
    
    // Market fields
    sector: randomChoice(['SaaS', 'Fintech', 'Healthcare', 'E-commerce', 'AI/ML', 'Marketplace']),
    tam_size_usd: tam,
    sam_size_usd: Math.round(sam),
    som_size_usd: Math.round(som),
    market_growth_rate_percent: randomBetween(5, 50),
    customer_count: randomBetween(0, 10000),
    customer_concentration_percent: randomBetween(5, 80),
    user_growth_rate_percent: randomBetween(-10, 300),
    net_dollar_retention_percent: randomBetween(70, 150),
    competition_intensity: randomBetween(1, 5),
    competitors_named_count: randomBetween(0, 20),
    dau_mau_ratio: randomFloat(0.1, 0.9),
    
    // People fields
    founders_count: randomBetween(1, 4),
    years_experience_avg: randomBetween(2, 20),
    domain_expertise_years_avg: randomBetween(1, 15),
    prior_startup_experience_count: randomBetween(0, 5),
    prior_successful_exits_count: randomBetween(0, 3),
    board_advisor_experience_score: randomBetween(1, 5),
    advisors_count: randomBetween(0, 10),
    team_diversity_percent: randomBetween(10, 60),
    key_person_dependency: Math.random() > 0.5
  };
};

// Generate different test scenarios
export const testScenarios = {
  bestCase: (): Partial<StartupData> => ({
    funding_stage: 'series_b',
    total_capital_raised_usd: 50000000,
    cash_on_hand_usd: 30000000,
    monthly_burn_usd: 400000,
    annual_revenue_run_rate: 25000000,
    revenue_growth_rate_percent: 200,
    gross_margin_percent: 85,
    ltv_cac_ratio: 4.5,
    investor_tier_primary: 'tier_1',
    has_debt: false,
    patent_count: 8,
    network_effects_present: true,
    has_data_moat: true,
    regulatory_advantage_present: true,
    tech_differentiation_score: 5,
    switching_cost_score: 5,
    brand_strength_score: 5,
    scalability_score: 5,
    product_stage: 'mature',
    product_retention_30d: 0.90,
    product_retention_90d: 0.80,
    sector: 'SaaS',
    tam_size_usd: 50000000000,
    sam_size_usd: 5000000000,
    som_size_usd: 500000000,
    market_growth_rate_percent: 35,
    customer_count: 5000,
    customer_concentration_percent: 15,
    user_growth_rate_percent: 150,
    net_dollar_retention_percent: 135,
    competition_intensity: 2,
    competitors_named_count: 5,
    dau_mau_ratio: 0.7,
    founders_count: 3,
    team_size_full_time: 120,
    years_experience_avg: 15,
    domain_expertise_years_avg: 12,
    prior_startup_experience_count: 3,
    prior_successful_exits_count: 2,
    board_advisor_experience_score: 5
  }),
  
  worstCase: (): Partial<StartupData> => ({
    funding_stage: 'Pre-seed',
    total_capital_raised_usd: 50000,
    cash_on_hand_usd: 10000,
    monthly_burn_usd: 15000,
    annual_revenue_run_rate: 0,
    revenue_growth_rate_percent: 0,
    gross_margin_percent: 0,
    ltv_cac_ratio: 0.2,
    investor_tier_primary: 'Angel',
    has_debt: true,
    patent_count: 0,
    network_effects_present: false,
    has_data_moat: false,
    regulatory_advantage_present: false,
    tech_differentiation_score: 1,
    switching_cost_score: 1,
    brand_strength_score: 1,
    scalability_score: 10,
    product_stage: 'MVP',
    product_retention_30d: 10,
    product_retention_90d: 2,
    sector: 'E-commerce',
    tam_size_usd: 500000000,
    sam_size_usd: 50000000,
    som_size_usd: 5000000,
    market_growth_rate_percent: -5,
    customer_count: 5,
    customer_concentration_percent: 100,
    user_growth_rate_percent: -20,
    net_dollar_retention_percent: 60,
    competition_intensity: 5,
    competitors_named_count: 50,
    dau_mau_ratio: 0.05,
    founders_count: 1,
    team_size_full_time: 2,
    years_experience_avg: 1,
    domain_expertise_years_avg: 0,
    prior_startup_experience_count: 0,
    prior_successful_exits_count: 0,
    board_advisor_experience_score: 1
  })
};