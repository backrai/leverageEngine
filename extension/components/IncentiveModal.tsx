import React, { useState, useEffect } from "react";
import type { Offer, Creator, Brand, NestedOfferList } from "../../shared/types";
import { supabase } from "../lib/supabase";
import { applyCouponCode } from "../lib/coupon-applier";
import { logAttributionEvent } from "../lib/attribution-logger";

interface IncentiveModalProps {
  brandId: string;
  referringCreatorId?: string;
  pathType: 'EARNED' | 'DISCOVERY';
  onClose: () => void;
}

export function IncentiveModal({ brandId, referringCreatorId, pathType, onClose }: IncentiveModalProps) {
  const [offers, setOffers] = useState<NestedOfferList[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedOffer, setSelectedOffer] = useState<Offer | null>(null);
  const [scraping, setScraping] = useState(false);

  useEffect(() => {
    loadOffers();
  }, [brandId, referringCreatorId, pathType]);

  /**
   * Triggers scraper to look for codes for this brand
   */
  async function triggerScraperForBrand(brandId: string): Promise<void> {
    try {
      setScraping(true);
      console.log('[backrAI] Triggering scraper for brand:', brandId);

      // Get dashboard API URL from environment or use default
      // Note: In production, this should be your deployed dashboard URL
      const apiUrl = process.env.PLASMO_PUBLIC_DASHBOARD_API_URL || 'http://localhost:3002';
      const scrapeEndpoint = `${apiUrl}/api/scrape-codes`;
      
      console.log('[backrAI] Calling scraper API:', scrapeEndpoint);

      const response = await fetch(scrapeEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ brandId }),
      });

      if (!response.ok) {
        throw new Error(`Scraper API returned ${response.status}`);
      }

      const result = await response.json();
      console.log('[backrAI] Scraper result:', result);

      if (result.success && result.offersFound > 0) {
        console.log(`[backrAI] Scraper found ${result.offersFound} codes for this brand`);
      } else {
        console.log('[backrAI] Scraper completed but no new codes found');
      }
    } catch (error) {
      console.error('[backrAI] Error triggering scraper:', error);
      // Don't show error to user - just log it
      // Scraper failure shouldn't break the user experience
    } finally {
      setScraping(false);
    }
  }

  async function loadOffers() {
    try {
      setLoading(true);
      
      // Build query based on path type
      let query = supabase
        .from('offers')
        .select(`
          *,
          creator:creators(*),
          brand:brands(*)
        `)
        .eq('brand_id', brandId)
        .eq('is_active', true);

      // Path A: Only show referring creator's offers
      if (pathType === 'EARNED' && referringCreatorId) {
        query = query.eq('creator_id', referringCreatorId);
      }

      let { data, error } = await query;

      if (error) {
        console.error('Error loading offers:', error);
        return;
      }

      // If no offers found, trigger scraper to look for codes
      if ((!data || data.length === 0) && brandId) {
        console.log('[backrAI] No offers found, triggering scraper for brand:', brandId);
        
        // Trigger scraper in background (don't await - let it run async)
        triggerScraperForBrand(brandId).then(() => {
          // After scraping completes, reload offers
          console.log('[backrAI] Scraper completed, reloading offers...');
          loadOffers();
        }).catch(err => {
          console.error('[backrAI] Scraper error:', err);
        });
      }

      // Transform to nested structure: Brand -> Creators -> Offers
      const nested: NestedOfferList[] = [];
      const brandMap = new Map<string, Brand>();
      const creatorMap = new Map<string, Map<string, Offer[]>>();

      data?.forEach((offer: any) => {
        const brand = offer.brand as Brand;
        const creator = offer.creator as Creator;
        
        // Explicitly map fields to ensure we use the correct values
        // Supabase returns snake_case, but we need to ensure code vs discount_amount are correct
        const offerData: Offer = {
          id: offer.id,
          creator_id: offer.creator_id,
          brand_id: offer.brand_id,
          code: offer.code, // This is the actual coupon code (e.g., "STUDENT15")
          discount_amount: offer.discount_amount, // This is the display text (e.g., "15% OFF")
          discount_type: offer.discount_type || 'percentage',
          is_active: offer.is_active,
          expires_at: offer.expires_at,
          created_at: offer.created_at,
          updated_at: offer.updated_at
        };

        // Debug: Log to ensure we have the right values
        console.log('[backrAI] Offer loaded:', {
          code: offerData.code,
          discount_amount: offerData.discount_amount,
          id: offerData.id
        });

        if (!brandMap.has(brand.id)) {
          brandMap.set(brand.id, brand);
          creatorMap.set(brand.id, new Map());
        }

        const creatorsForBrand = creatorMap.get(brand.id)!;
        if (!creatorsForBrand.has(creator.id)) {
          creatorsForBrand.set(creator.id, []);
        }

        creatorsForBrand.get(creator.id)!.push(offerData);
      });

      // Build nested structure
      brandMap.forEach((brand, brandId) => {
        const creators: { creator: Creator; offers: Offer[] }[] = [];
        creatorMap.get(brandId)!.forEach((offers, creatorId) => {
          const creator = data?.find((o: any) => o.creator.id === creatorId)?.creator as Creator;
          creators.push({ creator, offers });
        });
        nested.push({ brand, creators });
      });

      setOffers(nested);
    } catch (error) {
      console.error('Error in loadOffers:', error);
    } finally {
      setLoading(false);
    }
  }

  async function handleOfferClick(offer: Offer, creator: Creator) {
    try {
      setSelectedOffer(offer);
      
      // Use the actual offer code from the database (e.g., "ALEX15", "ALEX20")
      // This is what the user sees and what should be applied
      const couponCode = offer.code;
      
      // Debug: Log what we're about to apply
      console.log('[backrAI] Applying coupon code:', {
        offer_code: couponCode,
        discount_display: offer.discount_amount,
        offer_id: offer.id,
        creator_name: creator.display_name,
        affiliate_ref_code: creator.affiliate_ref_code
      });
      
      // Validate that we have an offer code
      if (!couponCode || couponCode.trim().length === 0) {
        console.error('[backrAI] ERROR: Offer code is missing!', {
          offer_id: offer.id,
          creator_name: creator.display_name
        });
        alert(`Error: Offer does not have a code. Please check the database.`);
        return;
      }
      
      // Apply the actual coupon code (from offer.code)
      await applyCouponCode(couponCode);
      
      // Log the attribution event (track affiliate_ref_code for attribution, but code used is offer.code)
      await logAttributionEvent({
        creatorId: creator.id,
        brandId: offer.brand_id,
        eventType: 'CHECKOUT_CLICK',
        pathType,
        offerCodeUsed: couponCode, // The actual code that was applied
        offerCodeBacked: creator.affiliate_ref_code // The creator's affiliate code for attribution
      });
      
      // Close modal immediately after applying
      onClose();
    } catch (error) {
      console.error('[backrAI] Error applying offer:', error);
      
      // Log detailed error information
      if (error instanceof Error) {
        console.error('[backrAI] Error details:', {
          message: error.message,
          name: error.name,
          stack: error.stack
        });
      } else if (error instanceof DOMException) {
        console.error('[backrAI] DOMException details:', {
          message: error.message,
          name: error.name,
          code: error.code
        });
      } else if (error && typeof error === 'object' && 'code' in error) {
        // Handle Supabase/API errors
        const apiError = error as { code?: string; message?: string; details?: string };
        console.error('[backrAI] API error:', {
          code: apiError.code,
          message: apiError.message,
          details: apiError.details
        });
        
        // Don't show alert for UUID errors - they're handled silently
        if (apiError.code === '22P02') {
          console.warn('[backrAI] UUID format error - this should be fixed now');
          return; // Exit silently
        }
      } else {
        console.error('[backrAI] Unknown error type:', typeof error, error);
      }
      
      // Don't show alert for DOMException (clipboard issues) - it's handled in coupon-applier
      // Don't show alert for API errors - they're logged but don't break user flow
      if (!(error instanceof DOMException) && (!error || typeof error !== 'object' || !('code' in error))) {
        alert('Failed to apply coupon code. Please try again.');
      }
    }
  }

  if (loading || scraping) {
    return (
      <div className="backrai-modal-overlay">
        <div className="backrai-modal">
          <div className="backrai-modal-header">
            <h2>Available Deals</h2>
            <button onClick={onClose} className="backrai-close-btn">×</button>
          </div>
          <div className="backrai-modal-body">
            {scraping ? (
              <div>
                <p>🔍 Searching for discount codes...</p>
                <p style={{ fontSize: '14px', color: '#666', marginTop: '8px' }}>
                  This may take a moment
                </p>
              </div>
            ) : (
              <p>Loading offers...</p>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (offers.length === 0) {
    return (
      <div className="backrai-modal-overlay">
        <div className="backrai-modal">
          <div className="backrai-modal-header">
            <h2>Available Deals</h2>
            <button onClick={onClose} className="backrai-close-btn">×</button>
          </div>
          <div className="backrai-modal-body">
            <p>No offers available at this time.</p>
          </div>
        </div>
      </div>
    );
  }

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
          <h2>Get the Best Deal & Support a Creator</h2>
          <button onClick={onClose} className="backrai-close-btn">×</button>
        </div>
        <div className="backrai-modal-body">
          {offers.map(({ brand, creators }) => (
            <div key={brand.id} className="backrai-brand-section">
              <h3 className="backrai-brand-name">{brand.name}</h3>
              {creators.map(({ creator, offers: creatorOffers }) => (
                <div key={creator.id} className="backrai-creator-section">
                  <div className="backrai-creator-info">
                    {creator.avatar_url && (
                      <img src={creator.avatar_url} alt={creator.display_name} className="backrai-creator-avatar" />
                    )}
                    <span className="backrai-creator-name">{creator.display_name}</span>
                  </div>
                  <div className="backrai-offers-list">
                    {creatorOffers.map((offer) => (
                      <button
                        key={offer.id}
                        className={`backrai-offer-btn ${selectedOffer?.id === offer.id ? 'selected' : ''}`}
                        onClick={() => handleOfferClick(offer, creator)}
                        disabled={selectedOffer !== null}
                      >
                        <div className="backrai-offer-code">{offer.code}</div>
                        <div className="backrai-offer-discount">{offer.discount_amount}</div>
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ))}
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
          max-width: 600px;
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
        .backrai-brand-section {
          margin-bottom: 24px;
        }
        .backrai-brand-name {
          font-size: 18px;
          font-weight: 600;
          margin: 0 0 16px 0;
        }
        .backrai-creator-section {
          margin-bottom: 16px;
          padding: 12px;
          background: #f9f9f9;
          border-radius: 8px;
        }
        .backrai-creator-info {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 12px;
        }
        .backrai-creator-avatar {
          width: 32px;
          height: 32px;
          border-radius: 50%;
        }
        .backrai-creator-name {
          font-weight: 500;
          font-size: 14px;
        }
        .backrai-offers-list {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }
        .backrai-offer-btn {
          padding: 12px 16px;
          border: 2px solid #e5e5e5;
          border-radius: 8px;
          background: white;
          cursor: pointer;
          transition: all 0.2s;
          display: flex;
          flex-direction: column;
          align-items: flex-start;
          min-width: 120px;
        }
        .backrai-offer-btn:hover:not(:disabled) {
          border-color: #007bff;
          background: #f0f8ff;
        }
        .backrai-offer-btn.selected {
          border-color: #007bff;
          background: #007bff;
          color: white;
        }
        .backrai-offer-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
        .backrai-offer-code {
          font-weight: 600;
          font-size: 14px;
        }
        .backrai-offer-discount {
          font-size: 12px;
          opacity: 0.8;
        }
      `}</style>
    </div>
  );
}

