// Shared TypeScript types for backrAI

export type PathType = 'EARNED' | 'DISCOVERY';
export type EventType = 'CHECKOUT_CLICK' | 'POST_PURCHASE_VOTE';

export interface Brand {
  id: string;
  name: string;
  domain_pattern: string;
  logo_url?: string;
  created_at: string;
  updated_at: string;
}

export interface Creator {
  id: string;
  display_name: string;
  avatar_url?: string;
  email?: string;
  affiliate_ref_code: string;
  created_at: string;
  updated_at: string;
}

export interface Offer {
  id: string;
  creator_id: string;
  brand_id: string;
  code: string;
  discount_amount: string;
  discount_type: 'percentage' | 'fixed';
  is_active: boolean;
  expires_at?: string;
  created_at: string;
  updated_at: string;
}

export interface AttributionEvent {
  id: string;
  user_id?: string;
  creator_id: string;
  brand_id: string;
  event_type: EventType;
  path_type: PathType;
  transaction_value?: number;
  offer_code_used?: string;
  offer_code_backed?: string;
  created_at: string;
}

export interface NestedOfferList {
  brand: Brand;
  creators: {
    creator: Creator;
    offers: Offer[];
  }[];
}

export interface LeverageData {
  lost_attribution_count: number;
  new_brand_discoveries: number;
  estimated_revenue: number;
  estimated_share: number;
}

