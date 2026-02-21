'use client';

import { useState, useEffect } from 'react';
import { LostAttributionTally } from './LostAttributionTally';
import { NewBrandLeads } from './NewBrandLeads';
import { RevenueTransparency } from './RevenueTransparency';
import type { LeverageData } from '@/lib/leverage-data';

interface LeverageDashboardProps {
  creatorId: string;
}

export function LeverageDashboard({ creatorId }: LeverageDashboardProps) {
  const [leverageData, setLeverageData] = useState<LeverageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadLeverageData();
  }, [creatorId]);

  async function loadLeverageData() {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/leverage?creator_id=${creatorId}`);
      if (!response.ok) {
        throw new Error('Failed to load leverage data');
      }

      const data = await response.json();
      setLeverageData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading leverage data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <h2 className="text-xl font-bold text-red-800 mb-2">Error</h2>
          <p className="text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  if (!leverageData) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Leverage Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Your data to negotiate better rates and partnerships
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Lost Attribution
            </h3>
            <p className="text-3xl font-bold text-red-600">
              {leverageData.lost_attribution_count}
            </p>
            <p className="text-sm text-gray-600 mt-2">
              Sales where you were backed but a different code was used
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              New Brand Leads
            </h3>
            <p className="text-3xl font-bold text-blue-600">
              {leverageData.new_brand_discoveries}
            </p>
            <p className="text-sm text-gray-600 mt-2">
              Brands you&apos;re driving sales for without partnerships
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Estimated Share
            </h3>
            <p className="text-3xl font-bold text-green-600">
              ${leverageData.estimated_share.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
              })}
            </p>
            <p className="text-sm text-gray-600 mt-2">
              Your estimated commission share
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <LostAttributionTally creatorId={creatorId} />
          <NewBrandLeads creatorId={creatorId} />
        </div>

        <div className="mt-6">
          <RevenueTransparency leverageData={leverageData} />
        </div>
      </div>
    </div>
  );
}

