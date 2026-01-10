import React from 'react';
import { useClaimAnalysis } from '@/hooks/useClaimData';
import { PolicyReferences } from './PolicyReferences';
import { ReasoningTrace } from './ReasoningTrace';

interface ClaimAnalysisPanelProps {
  claimId: string;
}

export function ClaimAnalysisPanel({ claimId }: ClaimAnalysisPanelProps) {
  const { data, isLoading, error, refetch } = useClaimAnalysis(claimId);
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <p className="ml-3 text-gray-600">Analyzing claim...</p>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-red-800">Analysis Failed</h3>
        <p className="text-red-600 mt-1">
          {error instanceof Error ? error.message : 'An error occurred'}
        </p>
        <button
          onClick={() => refetch()}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }
  
  if (!data?.data) {
    return null;
  }
  
  const analysis = data.data;
  
  return (
    <div className="space-y-6">
      <StatusBanner
        status={analysis.status}
        confidence={analysis.confidence_score}
      />
      
      <ActionCard
        action={analysis.recommended_action}
        requiredInfo={analysis.required_information}
      />
      
      {analysis.denial_reason && (
        <DenialReasonCard reason={analysis.denial_reason} />
      )}
      
      <PolicyReferences sections={analysis.policy_sections} />
      
      <ReasoningTrace steps={analysis.reasoning_steps} />
      
      {analysis.potential_issues && analysis.potential_issues.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-yellow-800 mb-2">
            Potential Issues
          </h3>
          <ul className="list-disc list-inside space-y-1 text-sm text-yellow-700">
            {analysis.potential_issues.map((issue, idx) => (
              <li key={idx}>{issue}</li>
            ))}
          </ul>
        </div>
      )}
      
      <div className="text-sm text-gray-500 border-t pt-4">
        <p>Analysis completed at {new Date(analysis.analysis_timestamp).toLocaleString()}</p>
        <p>Processing time: {data.processing_time_ms}ms</p>
        <p>Tokens used: {analysis.tokens_used}</p>
      </div>
    </div>
  );
}

function StatusBanner({ status, confidence }: { status: string; confidence: number }) {
  const statusColors = {
    approved: 'bg-green-100 border-green-400 text-green-800',
    denied: 'bg-red-100 border-red-400 text-red-800',
    pending_review: 'bg-yellow-100 border-yellow-400 text-yellow-800',
    needs_info: 'bg-blue-100 border-blue-400 text-blue-800',
  };
  
  const statusLabels = {
    approved: 'Recommended for Approval',
    denied: 'Recommended for Denial',
    pending_review: 'Requires Human Review',
    needs_info: 'Additional Information Needed',
  };
  
  return (
    <div className={`p-4 border-l-4 ${statusColors[status as keyof typeof statusColors]}`}>
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">
            {statusLabels[status as keyof typeof statusLabels]}
          </h3>
          <p className="text-sm mt-1">
            AI Confidence: {(confidence * 100).toFixed(1)}%
          </p>
        </div>
      </div>
    </div>
  );
}

function ActionCard({ action, requiredInfo }: { action: string; requiredInfo?: string[] }) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <h3 className="text-lg font-semibold mb-2">Recommended Action</h3>
      <p className="text-gray-700">{action}</p>
      {requiredInfo && requiredInfo.length > 0 && (
        <div className="mt-4">
          <h4 className="font-semibold text-sm mb-2">Required Information:</h4>
          <ul className="list-disc list-inside text-sm text-gray-600">
            {requiredInfo.map((info, idx) => (
              <li key={idx}>{info}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function DenialReasonCard({ reason }: { reason: string }) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
      <h3 className="text-lg font-semibold text-red-800 mb-2">Denial Reason</h3>
      <p className="text-red-700">{reason}</p>
    </div>
  );
}

