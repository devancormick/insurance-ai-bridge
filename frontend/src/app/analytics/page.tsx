"use client";

/**
 * Analytics Dashboard Page
 * Real-time analytics with data visualization
 */

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

interface AnalyticsData {
  total_claims: number;
  claims_processed: number;
  average_processing_time: number;
  claims_by_status: Record<string, number>;
  claims_by_month: Array<{ month: string; count: number }>;
  top_providers: Array<{ name: string; count: number }>;
}

export default function AnalyticsPage() {
  const [dateRange, setDateRange] = useState<'7d' | '30d' | '90d' | '1y'>('30d');

  // Fetch analytics data
  const { data: analytics, isLoading } = useQuery<AnalyticsData>({
    queryKey: ['analytics', dateRange],
    queryFn: async () => {
      const response = await apiClient.get(`/api/v1/analytics?range=${dateRange}`);
      return response.data;
    },
    refetchInterval: 30000 // Refresh every 30 seconds
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-lg">Loading analytics...</div>
      </div>
    );
  }

  if (!analytics) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>

            {/* Date Range Selector */}
            <div className="flex space-x-2">
              {(['7d', '30d', '90d', '1y'] as const).map((range) => (
                <button
                  key={range}
                  onClick={() => setDateRange(range)}
                  className={`px-4 py-2 rounded ${
                    dateRange === range
                      ? 'bg-blue-600 text-white'
                      : 'bg-white text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  {range === '7d' ? '7 Days' : range === '30d' ? '30 Days' : range === '90d' ? '90 Days' : '1 Year'}
                </button>
              ))}
            </div>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <MetricCard
              title="Total Claims"
              value={analytics.total_claims.toLocaleString()}
              trend="+12.5%"
              trendUp
            />
            <MetricCard
              title="Processed"
              value={analytics.claims_processed.toLocaleString()}
              trend="+8.3%"
              trendUp
            />
            <MetricCard
              title="Avg Processing Time"
              value={`${analytics.average_processing_time.toFixed(1)}s`}
              trend="-15.2%"
              trendUp
            />
            <MetricCard
              title="Success Rate"
              value="98.5%"
              trend="+0.5%"
              trendUp
            />
          </div>

          {/* Charts Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Claims by Status Chart */}
            <ChartCard title="Claims by Status">
              <div className="space-y-2">
                {Object.entries(analytics.claims_by_status).map(([status, count]) => (
                  <div key={status} className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700 capitalize">
                      {status}
                    </span>
                    <div className="flex items-center space-x-2">
                      <div className="w-32 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{
                            width: `${(count / analytics.total_claims) * 100}%`
                          }}
                        />
                      </div>
                      <span className="text-sm text-gray-600 w-16 text-right">
                        {count.toLocaleString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </ChartCard>

            {/* Claims by Month Chart */}
            <ChartCard title="Claims Over Time">
              <div className="h-64 flex items-end justify-between space-x-1">
                {analytics.claims_by_month.slice(-12).map((item, index) => {
                  const maxCount = Math.max(...analytics.claims_by_month.map((m) => m.count));
                  const height = (item.count / maxCount) * 100;

                  return (
                    <div key={index} className="flex-1 flex flex-col items-center">
                      <div
                        className="w-full bg-blue-600 rounded-t hover:bg-blue-700 transition-colors"
                        style={{ height: `${height}%` }}
                        title={`${item.month}: ${item.count}`}
                      />
                      <span className="text-xs text-gray-500 mt-2 transform -rotate-45 origin-top-left">
                        {new Date(item.month).toLocaleDateString('en-US', {
                          month: 'short'
                        })}
                      </span>
                    </div>
                  );
                })}
              </div>
            </ChartCard>

            {/* Top Providers */}
            <ChartCard title="Top Providers">
              <div className="space-y-3">
                {analytics.top_providers.slice(0, 10).map((provider, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">
                      {index + 1}. {provider.name}
                    </span>
                    <span className="text-sm text-gray-600">
                      {provider.count.toLocaleString()} claims
                    </span>
                  </div>
                ))}
              </div>
            </ChartCard>

            {/* Export Options */}
            <ChartCard title="Export Data">
              <div className="space-y-3">
                <button className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                  Export to PDF
                </button>
                <button className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
                  Export to Excel
                </button>
                <button className="w-full px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700">
                  Export to CSV
                </button>
              </div>
            </ChartCard>
          </div>
        </div>
      </div>
    </div>
  );
}

interface MetricCardProps {
  title: string;
  value: string;
  trend: string;
  trendUp?: boolean;
}

function MetricCard({ title, value, trend, trendUp }: MetricCardProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-sm font-medium text-gray-500 mb-2">{title}</h3>
      <div className="flex items-baseline justify-between">
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        <span
          className={`text-sm font-medium ${
            trendUp ? 'text-green-600' : 'text-red-600'
          }`}
        >
          {trend}
        </span>
      </div>
    </div>
  );
}

interface ChartCardProps {
  title: string;
  children: React.ReactNode;
}

function ChartCard({ title, children }: ChartCardProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      {children}
    </div>
  );
}


