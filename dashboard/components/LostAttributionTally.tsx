'use client';

import { useState, useEffect } from 'react';
import type { LostAttributionEvent } from '@/lib/leverage-data';

interface LostAttributionTallyProps {
  creatorId: string;
}

export function LostAttributionTally({ creatorId }: LostAttributionTallyProps) {
  const [events, setEvents] = useState<LostAttributionEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadEvents();
  }, [creatorId]);

  async function loadEvents() {
    try {
      const response = await fetch(`/api/lost-attribution?creator_id=${creatorId}`);
      if (!response.ok) {
        throw new Error('Failed to load lost attribution events');
      }

      const data = await response.json();
      setEvents(data);
    } catch (error) {
      console.error('Error loading lost attribution:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4">Lost Attribution Tally</h2>
        <p className="text-gray-600">Loading...</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold mb-4">Lost Attribution Tally</h2>
      <p className="text-sm text-gray-600 mb-4">
        Sales where you were backed post-purchase but a different code was used at checkout.
      </p>

      {events.length === 0 ? (
        <p className="text-gray-500 text-center py-8">No lost attribution events yet.</p>
      ) : (
        <div className="space-y-4">
          {events.map((event) => (
            <div
              key={event.id}
              className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition"
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <p className="font-semibold text-gray-900">{event.brand_name}</p>
                  <p className="text-sm text-gray-600">
                    {new Date(event.created_at).toLocaleDateString()}
                  </p>
                </div>
                {event.transaction_value && (
                  <p className="font-semibold text-green-600">
                    ${event.transaction_value.toFixed(2)}
                  </p>
                )}
              </div>
              <div className="flex gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Code Used: </span>
                  <span className="font-mono font-semibold">{event.offer_code_used}</span>
                </div>
                <div>
                  <span className="text-gray-500">You Backed: </span>
                  <span className="font-mono font-semibold text-blue-600">
                    {event.offer_code_backed}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

