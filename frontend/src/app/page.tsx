'use client';

import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';

export default function Home() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-white">
      <div className="max-w-7xl mx-auto px-4 py-16 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Insurance AI Bridge System
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            AI-powered claim analysis and processing. Reduce case research time from 18 minutes to under 2 minutes.
          </p>
          
          <div className="flex justify-center space-x-4 mb-16">
            {isAuthenticated ? (
              <>
                <Button
                  variant="primary"
                  size="lg"
                  onClick={() => router.push('/dashboard')}
                >
                  Go to Dashboard
                </Button>
                <Button
                  variant="secondary"
                  size="lg"
                  onClick={() => router.push('/claims')}
                >
                  View Claims
                </Button>
              </>
            ) : (
              <Button
                variant="primary"
                size="lg"
                onClick={() => router.push('/auth/signin')}
              >
                Sign In to Get Started
              </Button>
            )}
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                AI-Powered Analysis
              </h3>
              <p className="text-sm text-gray-600">
                Leverage OpenAI and Anthropic LLMs for intelligent claim analysis with structured outputs.
              </p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                HIPAA Compliant
              </h3>
              <p className="text-sm text-gray-600">
                Zero-retention PII handling with comprehensive audit logging and encryption.
              </p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Multi-Source Integration
              </h3>
              <p className="text-sm text-gray-600">
                Aggregate data from legacy databases, SOAP APIs, and SharePoint documents.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


