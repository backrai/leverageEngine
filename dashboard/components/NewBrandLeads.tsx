'use client';

import { useState, useEffect } from 'react';
import type { NewBrandLead } from '@/lib/leverage-data';

interface NewBrandLeadsProps {
  creatorId: string;
}

export function NewBrandLeads({ creatorId }: NewBrandLeadsProps) {
  const [leads, setLeads] = useState<NewBrandLead[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLeads();
  }, [creatorId]);

  async function loadLeads() {
    try {
      const response = await fetch(`/api/new-brand-leads?creator_id=${creatorId}`);
      if (!response.ok) {
        throw new Error('Failed to load new brand leads');
      }

      const data = await response.json();
      setLeads(data);
    } catch (error) {
      console.error('Error loading new brand leads:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4">New Brand Leads</h2>
        <p className="text-gray-600">Loading...</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold mb-4">New Brand Leads</h2>
      <p className="text-sm text-gray-600 mb-4">
        Brands you're driving sales for where you don't have an official partnership yet.
      </p>

      {leads.length === 0 ? (
        <p className="text-gray-500 text-center py-8">No new brand leads yet.</p>
      ) : (
        <div className="space-y-4">
          {leads.map((lead) => (
            <div
              key={lead.brand_id}
              className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition"
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <p className="font-semibold text-gray-900">{lead.brand_name}</p>
                  <p className="text-sm text-gray-600">
                    {lead.attribution_count} {lead.attribution_count === 1 ? 'attribution' : 'attributions'}
                  </p>
                </div>
                <p className="font-semibold text-green-600">
                  ${lead.total_value.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                  })}
                </p>
              </div>
              <button className="mt-2 text-sm text-blue-600 hover:text-blue-800 font-medium">
                Reach out to {lead.brand_name} →
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

