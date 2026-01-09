/** TypeScript types for claim-related data structures. */

export interface ClaimAnalysisRequest {
  claim_id: string;
  include_member_history?: boolean;
  include_policy_docs?: boolean;
}

export interface PolicyReference {
  document_name: string;
  section_number: string;
  section_title: string;
  relevant_text: string;
  relevance_score: number;
}

export interface ReasoningStep {
  step_number: number;
  description: string;
  data_sources: string[];
}

export interface ClaimAnalysis {
  claim_id: string;
  analysis_timestamp: string;
  status: 'approved' | 'denied' | 'pending_review' | 'needs_info';
  denial_reason?: string;
  policy_sections: PolicyReference[];
  recommended_action: string;
  required_information?: string[];
  confidence_score: number;
  reasoning_steps: ReasoningStep[];
  potential_issues: string[];
  tokens_used: number;
}

export interface ClaimAnalysisResponse {
  success: boolean;
  data?: ClaimAnalysis;
  error?: string;
  processing_time_ms: number;
}

