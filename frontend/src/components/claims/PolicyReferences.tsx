import React from 'react';
import { PolicyReference } from '@/types/claim';

interface PolicyReferencesProps {
  sections: PolicyReference[];
}

export function PolicyReferences({ sections }: PolicyReferencesProps) {
  if (!sections || sections.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-600">
        No policy references found.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Policy References</h3>
      {sections.map((section, index) => (
        <div
          key={index}
          className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          <div className="flex items-start justify-between mb-2">
            <div>
              <h4 className="font-semibold text-gray-900">
                {section.document_name}
              </h4>
              <p className="text-sm text-gray-600">
                Section {section.section_number}: {section.section_title}
              </p>
            </div>
            <div className="flex items-center">
              <span className="text-xs font-medium text-primary-600 bg-primary-50 px-2 py-1 rounded">
                {(section.relevance_score * 100).toFixed(0)}% relevant
              </span>
            </div>
          </div>
          <div className="mt-3 p-3 bg-gray-50 rounded text-sm text-gray-700">
            <p className="font-medium mb-1">Relevant Text:</p>
            <p className="text-gray-600">{section.relevant_text}</p>
          </div>
        </div>
      ))}
    </div>
  );
}

