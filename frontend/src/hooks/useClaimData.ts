import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { ClaimAnalysisResponse, ClaimAnalysisRequest } from '@/types/claim';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function useClaimAnalysis(claimId: string) {
  return useQuery({
    queryKey: ['claim-analysis', claimId],
    queryFn: async () => {
      const response = await axios.post<ClaimAnalysisResponse>(
        `${API_URL}/api/v1/claims/${claimId}/analyze`,
        {
          claim_id: claimId,
          include_member_history: true,
          include_policy_docs: true,
        } as ClaimAnalysisRequest
      );
      return response.data;
    },
    staleTime: Infinity,
    gcTime: 1000 * 60 * 30, // 30 minutes (formerly cacheTime)
    retry: 1,
    enabled: !!claimId,
  });
}

export function useUpdateClaim() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ claimId, data }: { claimId: string; data: any }) => {
      const response = await axios.patch(
        `${API_URL}/api/v1/claims/${claimId}`,
        data
      );
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['claim-analysis', variables.claimId] });
      queryClient.invalidateQueries({ queryKey: ['claims'] });
    },
  });
}

