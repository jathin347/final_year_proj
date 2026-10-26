export interface ExtractedClaim {
  claim_id: string;
  claim_text: string;
  importance: 'HIGH' | 'MEDIUM' | 'LOW';
  category: string;
  named_entities: string[];
  relevant_dates: string[];
  relevant_locations: string[];
  search_queries: string[];
  verification_status: 'SUPPORTED' | 'CONTRADICTED' | 'MISLEADING' | 'CONFLICTING' | 'INSUFFICIENT' | 'UNVERIFIED';
  supporting_evidence_ids: string[];
  contradicting_evidence_ids: string[];
  explanation?: string;
}

export interface FactCheckItem {
  id: string;
  claim_reviewed: string;
  fact_checker_publisher: string;
  publisher_site?: string;
  review_title: string;
  review_url: string;
  publication_date?: string;
  original_rating: string;
  normalized_verdict: 'FALSE' | 'TRUE' | 'MIXED' | 'UNPROVEN';
  claim_date?: string;
  retrieval_timestamp: string;
}

export interface NewsArticleItem {
  id: string;
  title: string;
  publisher: string;
  domain: string;
  url: string;
  publication_date?: string;
  snippet?: string;
  search_query: string;
  retrieval_timestamp: string;
  stance: 'supporting' | 'contradicting' | 'contextual' | 'neutral';
  relevance_score: number;
  is_syndicated_duplicate: boolean;
}

export interface CredibilityFactor {
  factor_name: string;
  score: number;
  weight: number;
  description: string;
  status: 'Observed' | 'Partially observed' | 'Unobserved';
}

export interface SourceCredibilityReport {
  domain?: string;
  publisher_name?: string;
  overall_score?: number | null;
  assessment_status: 'Assessed' | 'Partially assessed' | 'Insufficient source information' | 'Assessment unavailable';
  factors: CredibilityFactor[];
  missing_signals: string[];
  disclaimer: string;
}

export interface TextModelAnalysis {
  model_name: string;
  model_version: string;
  prediction: string;
  confidence: number;
  stylometric_signals: Record<string, any>;
  key_attribution_tokens: Array<{
    token: string;
    attribution_weight: number;
    indicator_type: string;
  }>;
  inference_time_ms: number;
  limitations: string;
}

export interface ImageModelAnalysis {
  has_image: boolean;
  image_format?: string;
  image_dimensions?: string;
  image_text_relevance_score?: number | null;
  visual_context_summary?: string;
  flags: string[];
  inference_time_ms?: number;
  limitations: string;
}

export interface DecisionFusionReport {
  final_assessment: 'Supported by available evidence' | 'Contradicted by available evidence' | 'Misleading or missing context' | 'Conflicting evidence' | 'Insufficient evidence' | 'Analysis unavailable';
  explanation: string;
  uncertainty_level: 'Low' | 'Moderate' | 'High';
  supporting_evidence_count: number;
  contradicting_evidence_count: number;
  fact_check_count: number;
  evidence_coverage: 'Robust' | 'Moderate' | 'Sparse' | 'None';
  decision_rules_applied: string[];
}

export interface AnalysisResponse {
  id: string;
  headline: string;
  article_url?: string;
  publisher?: string;
  domain?: string;
  author?: string;
  published_date?: string;
  article_summary?: string;
  final_assessment: string;
  assessment_explanation: string;
  uncertainty_level: string;
  claims: ExtractedClaim[];
  fact_checks: FactCheckItem[];
  news_articles: NewsArticleItem[];
  source_credibility: SourceCredibilityReport;
  text_analysis: TextModelAnalysis;
  image_analysis: ImageModelAnalysis;
  decision_fusion: DecisionFusionReport;
  status: string;
  provider_status: Record<string, string>;
  latency_breakdown_ms: Record<string, number>;
  total_latency_ms: number;
  retrieval_timestamp: string;
  created_at: string;
}

export interface AnalysisHistorySummary {
  id: string;
  headline: string;
  article_url?: string;
  domain?: string;
  final_assessment: string;
  source_credibility_score?: number | null;
  total_latency_ms: number;
  created_at: string;
}

export interface PaginatedHistoryResponse {
  items: AnalysisHistorySummary[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface ProviderItem {
  name: string;
  purpose: string;
  configured: boolean;
  status: string;
  documentation: string;
}
