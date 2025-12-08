import React, { useState, useEffect } from "react";
import type { Creator } from "../../shared/types";
import { supabase } from "../lib/supabase";
import { logAttributionEvent } from "../lib/attribution-logger";
import { getBrowsingHistory } from "../lib/storage";

interface AttributionModalProps {
  brandId: string;
  pathType: 'EARNED' | 'DISCOVERY';
  onClose: () => void;
}

export function AttributionModal({ brandId, pathType, onClose }: AttributionModalProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [suggestedCreators, setSuggestedCreators] = useState<Creator[]>([]);
  const [searchResults, setSearchResults] = useState<Creator[]>([]);
  const [selectedCreator, setSelectedCreator] = useState<Creator | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadSuggestedCreators();
  }, [brandId]);

  async function loadSuggestedCreators() {
    try {
      // Get browsing history
      const history = await getBrowsingHistory();
      
      // Get unique creator IDs from history
      const creatorIds = [...new Set(history.map(h => h.creatorId))];
      
      if (creatorIds.length === 0) {
        // If no history, get creators with offers for this brand
        const { data } = await supabase
          .from('offers')
          .select('creator:creators(*)')
          .eq('brand_id', brandId)
          .eq('is_active', true)
          .limit(5);
        
        if (data) {
          const creators = data.map((d: any) => d.creator).filter(Boolean);
          setSuggestedCreators(creators);
        }
        return;
      }

      // Fetch creator details
      const { data } = await supabase
        .from('creators')
        .select('*')
        .in('id', creatorIds.slice(0, 5));

      if (data) {
        setSuggestedCreators(data);
      }
    } catch (error) {
      console.error('Error loading suggested creators:', error);
    }
  }

  async function handleSearch(query: string) {
    setSearchQuery(query);
    
    if (query.length < 2) {
      setSearchResults([]);
      return;
    }

    try {
      const { data, error } = await supabase
        .from('creators')
        .select('*')
        .ilike('display_name', `%${query}%`)
        .limit(10);

      if (error) {
        console.error('Search error:', error);
        return;
      }

      setSearchResults(data || []);
    } catch (error) {
      console.error('Error searching creators:', error);
    }
  }

  async function handleSubmit() {
    if (!selectedCreator) {
      alert('Please select a creator who inspired your purchase.');
      return;
    }

    try {
      setSubmitting(true);
      
      await logAttributionEvent({
        creatorId: selectedCreator.id,
        brandId,
        eventType: 'POST_PURCHASE_VOTE',
        pathType,
        offerCodeBacked: selectedCreator.affiliate_ref_code
      });

      // Show success message
      alert('Thank you for supporting ' + selectedCreator.display_name + '!');
      onClose();
    } catch (error) {
      console.error('Error submitting attribution:', error);
      alert('Failed to submit attribution. Please try again.');
    } finally {
      setSubmitting(false);
    }
  }

  const displayCreators = searchQuery.length >= 2 ? searchResults : suggestedCreators;

  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    // Only close if clicking the overlay itself, not the modal content
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="backrai-modal-overlay" onClick={handleOverlayClick}>
      <div className="backrai-modal" onClick={(e) => e.stopPropagation()}>
        <div className="backrai-modal-header">
          <h2>Success! Order Confirmed</h2>
          <button onClick={onClose} className="backrai-close-btn">×</button>
        </div>
        <div className="backrai-modal-body">
          <p className="backrai-prompt">Who inspired this purchase?</p>
          
          <div className="backrai-search-container">
            <input
              type="text"
              placeholder="Search for a creator..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="backrai-search-input"
            />
          </div>

          <div className="backrai-creators-list">
            {displayCreators.length === 0 && searchQuery.length >= 2 && (
              <p className="backrai-no-results">No creators found.</p>
            )}
            {displayCreators.map((creator) => (
              <button
                key={creator.id}
                className={`backrai-creator-card ${selectedCreator?.id === creator.id ? 'selected' : ''}`}
                onClick={() => setSelectedCreator(creator)}
              >
                {creator.avatar_url && (
                  <img src={creator.avatar_url} alt={creator.display_name} className="backrai-creator-avatar" />
                )}
                <span className="backrai-creator-name">{creator.display_name}</span>
              </button>
            ))}
          </div>

          <div className="backrai-modal-footer">
            <button
              onClick={handleSubmit}
              disabled={!selectedCreator || submitting}
              className="backrai-submit-btn"
            >
              {submitting ? 'Submitting...' : 'Submit'}
            </button>
            <button onClick={onClose} className="backrai-skip-btn">
              Skip
            </button>
          </div>
        </div>
      </div>
      <style>{`
        .backrai-modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 999999;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        .backrai-modal {
          background: white;
          border-radius: 12px;
          max-width: 500px;
          width: 90%;
          max-height: 80vh;
          overflow-y: auto;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }
        .backrai-modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 20px;
          border-bottom: 1px solid #e5e5e5;
        }
        .backrai-modal-header h2 {
          margin: 0;
          font-size: 20px;
          font-weight: 600;
        }
        .backrai-close-btn {
          background: none;
          border: none;
          font-size: 28px;
          cursor: pointer;
          color: #666;
          padding: 0;
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .backrai-close-btn:hover {
          color: #000;
        }
        .backrai-modal-body {
          padding: 20px;
        }
        .backrai-prompt {
          font-size: 16px;
          margin: 0 0 16px 0;
          color: #333;
        }
        .backrai-search-container {
          margin-bottom: 20px;
        }
        .backrai-search-input {
          width: 100%;
          padding: 12px;
          border: 1px solid #e5e5e5;
          border-radius: 8px;
          font-size: 14px;
          box-sizing: border-box;
        }
        .backrai-search-input:focus {
          outline: none;
          border-color: #007bff;
        }
        .backrai-creators-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
          margin-bottom: 20px;
          max-height: 300px;
          overflow-y: auto;
        }
        .backrai-creator-card {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px;
          border: 2px solid #e5e5e5;
          border-radius: 8px;
          background: white;
          cursor: pointer;
          transition: all 0.2s;
          text-align: left;
          width: 100%;
        }
        .backrai-creator-card:hover {
          border-color: #007bff;
          background: #f0f8ff;
        }
        .backrai-creator-card.selected {
          border-color: #007bff;
          background: #007bff;
          color: white;
        }
        .backrai-creator-avatar {
          width: 40px;
          height: 40px;
          border-radius: 50%;
        }
        .backrai-creator-name {
          font-weight: 500;
          font-size: 14px;
        }
        .backrai-no-results {
          text-align: center;
          color: #666;
          padding: 20px;
        }
        .backrai-modal-footer {
          display: flex;
          gap: 12px;
          justify-content: flex-end;
        }
        .backrai-submit-btn {
          padding: 12px 24px;
          background: #007bff;
          color: white;
          border: none;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
          font-size: 14px;
        }
        .backrai-submit-btn:hover:not(:disabled) {
          background: #0056b3;
        }
        .backrai-submit-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
        .backrai-skip-btn {
          padding: 12px 24px;
          background: transparent;
          color: #666;
          border: 1px solid #e5e5e5;
          border-radius: 8px;
          font-weight: 500;
          cursor: pointer;
          font-size: 14px;
        }
        .backrai-skip-btn:hover {
          background: #f5f5f5;
        }
      `}</style>
    </div>
  );
}

