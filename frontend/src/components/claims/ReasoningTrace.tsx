import React from 'react';
import { ReasoningStep } from '@/types/claim';

interface ReasoningTraceProps {
  steps: ReasoningStep[];
}

export function ReasoningTrace({ steps }: ReasoningTraceProps) {
  if (!steps || steps.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">AI Reasoning Process</h3>
      <div className="space-y-3">
        {steps.map((step) => (
          <div
            key={step.step_number}
            className="bg-white border-l-4 border-primary-500 rounded p-4 shadow-sm"
          >
            <div className="flex items-start">
              <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center mr-3">
                <span className="text-sm font-semibold text-primary-700">
                  {step.step_number}
                </span>
              </div>
              <div className="flex-1">
                <p className="text-gray-900 mb-2">{step.description}</p>
                {step.data_sources && step.data_sources.length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs text-gray-500 mb-1">Data Sources:</p>
                    <div className="flex flex-wrap gap-2">
                      {step.data_sources.map((source, idx) => (
                        <span
                          key={idx}
                          className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-800"
                        >
                          {source}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

