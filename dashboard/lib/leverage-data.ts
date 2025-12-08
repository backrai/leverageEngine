// Leverage data calculation utilities

import { createServerClient } from './supabase';

export interface LeverageData {
  lost_attribution_count: number;
  new_brand_discoveries: number;
  estimated_revenue: number;
  estimated_share: number;
}

export interface LostAttributionEvent {
  id: string;
  brand_name: string;
  offer_code_used: string | null;
  offer_code_backed: string | null;
  transaction_value: number | null;
  created_at: string;
}

export interface NewBrandLead {
  brand_id: string;
  brand_name: string;
  attribution_count: number;
  total_value: number;
}

/**
 * Get leverage data for a creator
 */
export async function getLeverageData(creatorId: string): Promise<LeverageData> {
  const supabase = createServerClient();

  // Get all attribution events for this creator
  const { data: events, error } = await supabase
    .from('attribution_events')
    .select(`
      *,
      brand:brands(name)
    `)
    .eq('creator_id', creatorId);

  if (error) {
    throw new Error(`Failed to fetch attribution events: ${error.message}`);
  }

  if (!events || events.length === 0) {
    return {
      lost_attribution_count: 0,
      new_brand_discoveries: 0,
      estimated_revenue: 0,
      estimated_share: 0
    };
  }

  // Calculate lost attribution count
  // Lost attribution = POST_PURCHASE_VOTE where offer_code_used != offer_code_backed
  const lostAttribution = events.filter(
    (e) =>
      e.event_type === 'POST_PURCHASE_VOTE' &&
      e.offer_code_used &&
      e.offer_code_backed &&
      e.offer_code_used !== e.offer_code_backed
  );

  // Calculate new brand discoveries
  // Get all brands this creator was backed for
  const backedBrands = new Set(
    events
      .filter((e) => e.brand_id)
      .map((e) => e.brand_id!)
  );

  // Get brands where creator has active offers (official partnerships)
  const { data: officialBrands } = await supabase
    .from('offers')
    .select('brand_id')
    .eq('creator_id', creatorId)
    .eq('is_active', true);

  const officialBrandIds = new Set(
    (officialBrands || []).map((o) => o.brand_id)
  );

  // New brand discoveries = brands backed but not officially partnered
  const newBrandIds = Array.from(backedBrands).filter(
    (id) => !officialBrandIds.has(id)
  );

  // Get new brand details
  const { data: newBrands } = await supabase
    .from('brands')
    .select('id, name')
    .in('id', newBrandIds);

  // Calculate estimated revenue
  const totalValue = events.reduce((sum, e) => {
    return sum + (e.transaction_value || 0);
  }, 0);

  // Estimate share (assuming 5-10% commission rate)
  const estimatedShare = totalValue * 0.075; // 7.5% average

  return {
    lost_attribution_count: lostAttribution.length,
    new_brand_discoveries: newBrandIds.length,
    estimated_revenue: totalValue,
    estimated_share
  };
}

/**
 * Get lost attribution events with details
 */
export async function getLostAttributionEvents(
  creatorId: string
): Promise<LostAttributionEvent[]> {
  const supabase = createServerClient();

  const { data, error } = await supabase
    .from('attribution_events')
    .select(`
      id,
      offer_code_used,
      offer_code_backed,
      transaction_value,
      created_at,
      brand:brands(name)
    `)
    .eq('creator_id', creatorId)
    .eq('event_type', 'POST_PURCHASE_VOTE')
    .not('offer_code_used', 'is', null)
    .not('offer_code_backed', 'is', null)
    .neq('offer_code_used', 'offer_code_backed')
    .order('created_at', { ascending: false });

  if (error) {
    throw new Error(`Failed to fetch lost attribution: ${error.message}`);
  }

  return (data || []).map((e: any) => ({
    id: e.id,
    brand_name: e.brand?.name || 'Unknown',
    offer_code_used: e.offer_code_used,
    offer_code_backed: e.offer_code_backed,
    transaction_value: e.transaction_value,
    created_at: e.created_at
  }));
}

/**
 * Get new brand leads
 */
export async function getNewBrandLeads(
  creatorId: string
): Promise<NewBrandLead[]> {
  const supabase = createServerClient();

  // Get all brands this creator was backed for
  const { data: allEvents } = await supabase
    .from('attribution_events')
    .select('brand_id, transaction_value')
    .eq('creator_id', creatorId)
    .not('brand_id', 'is', null);

  if (!allEvents) {
    return [];
  }

  // Get official brand partnerships
  const { data: officialBrands } = await supabase
    .from('offers')
    .select('brand_id')
    .eq('creator_id', creatorId)
    .eq('is_active', true);

  const officialBrandIds = new Set(
    (officialBrands || []).map((o) => o.brand_id)
  );

  // Group by brand and filter out official partnerships
  const brandMap = new Map<string, { count: number; totalValue: number }>();

  allEvents.forEach((e) => {
    if (e.brand_id && !officialBrandIds.has(e.brand_id)) {
      const existing = brandMap.get(e.brand_id) || { count: 0, totalValue: 0 };
      brandMap.set(e.brand_id, {
        count: existing.count + 1,
        totalValue: existing.totalValue + (e.transaction_value || 0)
      });
    }
  });

  // Get brand names
  const brandIds = Array.from(brandMap.keys());
  const { data: brands } = await supabase
    .from('brands')
    .select('id, name')
    .in('id', brandIds);

  const brandNameMap = new Map(
    (brands || []).map((b) => [b.id, b.name])
  );

  return Array.from(brandMap.entries()).map(([brandId, stats]) => ({
    brand_id: brandId,
    brand_name: brandNameMap.get(brandId) || 'Unknown',
    attribution_count: stats.count,
    total_value: stats.totalValue
  }));
}

