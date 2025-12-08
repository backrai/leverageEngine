'use client';

import { useState, useEffect } from 'react';
import { LeverageDashboard } from '@/components/LeverageDashboard';

export default function Home() {
  const [creatorId, setCreatorId] = useState<string>('');

  // In production, this would come from authentication
  // For MVP, we'll use a query parameter or localStorage
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const id = params.get('creator_id') || localStorage.getItem('creator_id');
    if (id) {
      setCreatorId(id);
      localStorage.setItem('creator_id', id);
    }
  }, []);

  if (!creatorId) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
          <h1 className="text-2xl font-bold mb-4">backrAI Creator Dashboard</h1>
          <p className="text-gray-600 mb-4">
            Please provide your creator ID to view your leverage data.
          </p>
          <input
            type="text"
            placeholder="Creator ID"
            value={creatorId}
            onChange={(e) => setCreatorId(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-md mb-4"
          />
          <button
            onClick={() => {
              if (creatorId) {
                localStorage.setItem('creator_id', creatorId);
                window.location.reload();
              }
            }}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
          >
            Load Dashboard
          </button>
        </div>
      </div>
    );
  }

  return <LeverageDashboard creatorId={creatorId} />;
}

