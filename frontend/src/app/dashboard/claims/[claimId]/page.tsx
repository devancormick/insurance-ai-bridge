'use client';

import { useParams } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { ClaimAnalysisPanel } from '@/components/claims/ClaimAnalysisPanel';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';

export default function ClaimDetailPage() {
  const params = useParams();
  const claimId = params?.claimId as string;
  const { isAuthenticated, isLoading } = useAuth(true);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingSpinner size="lg" text="Loading..." />
      </div>
    );
  }

  if (!isAuthenticated || !claimId) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          Claim Analysis: {claimId}
        </h1>
        <ClaimAnalysisPanel claimId={claimId} />
      </div>
    </div>
  );
}

