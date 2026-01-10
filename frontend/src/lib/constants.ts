/** Application constants. */

export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/v1/auth/login',
    ME: '/api/v1/auth/me',
    REGISTER: '/api/v1/auth/register',
  },
  CLAIMS: {
    ANALYZE: (claimId: string) => `/api/v1/claims/${claimId}/analyze`,
    GET: (claimId: string) => `/api/v1/claims/${claimId}`,
  },
  POLICIES: {
    GET: (policyId: string) => `/api/v1/policies/${policyId}`,
    MEMBERS: (policyId: string) => `/api/v1/policies/${policyId}/members`,
  },
  MEMBERS: {
    GET: (memberId: string) => `/api/v1/members/${memberId}`,
    CLAIMS: (memberId: string) => `/api/v1/members/${memberId}/claims`,
  },
  HEALTH: '/health',
  METRICS: '/metrics',
} as const;

export const QUERY_KEYS = {
  CLAIM_ANALYSIS: (claimId: string) => ['claim-analysis', claimId],
  CLAIM: (claimId: string) => ['claim', claimId],
  POLICY: (policyId: string) => ['policy', policyId],
  MEMBER: (memberId: string) => ['member', memberId],
  MEMBER_CLAIMS: (memberId: string) => ['member-claims', memberId],
  USER: ['user'],
} as const;

export const ROUTES = {
  HOME: '/',
  DASHBOARD: '/dashboard',
  AUTH: {
    SIGNIN: '/auth/signin',
    ERROR: '/auth/error',
  },
  CLAIMS: {
    LIST: '/claims',
    DETAIL: (claimId: string) => `/claims/${claimId}`,
  },
} as const;

