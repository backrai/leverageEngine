'use client';

import type { LeverageData } from '@/lib/leverage-data';

interface RevenueTransparencyProps {
  leverageData: LeverageData;
}

export function RevenueTransparency({ leverageData }: RevenueTransparencyProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold mb-4">Revenue Transparency</h2>
      <p className="text-sm text-gray-600 mb-6">
        Estimated revenue impact based on your attribution data.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-blue-50 rounded-lg p-6">
          <h3 className="text-sm font-medium text-blue-900 mb-2">
            Total Revenue Generated
          </h3>
          <p className="text-4xl font-bold text-blue-600 mb-2">
            ${leverageData.estimated_revenue.toLocaleString('en-US', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2
            })}
          </p>
          <p className="text-sm text-blue-700">
            Total value of sales you helped generate
          </p>
        </div>

        <div className="bg-green-50 rounded-lg p-6">
          <h3 className="text-sm font-medium text-green-900 mb-2">
            Your Estimated Share
          </h3>
          <p className="text-4xl font-bold text-green-600 mb-2">
            ${leverageData.estimated_share.toLocaleString('en-US', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2
            })}
          </p>
          <p className="text-sm text-green-700">
            Estimated commission at 7.5% average rate
          </p>
        </div>
      </div>

      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <p className="text-sm text-gray-600">
          <strong>Note:</strong> These estimates are based on transaction values from attribution events.
          Actual commission rates may vary by brand and partnership terms. Use this data as leverage
          when negotiating rates with brands.
        </p>
      </div>
    </div>
  );
}

