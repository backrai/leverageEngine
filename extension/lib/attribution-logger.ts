// Attribution event logging

import { supabase } from "./supabase";
import { getUserId } from "./storage";
import type { EventType, PathType } from "../../shared/types";

export interface AttributionEventData {
  creatorId: string;
  brandId: string;
  eventType: EventType;
  pathType: PathType;
  transactionValue?: number;
  offerCodeUsed?: string;
  offerCodeBacked?: string;
}

/**
 * Logs an attribution event to Supabase
 */
export async function logAttributionEvent(data: AttributionEventData): Promise<void> {
  try {
    const userId = await getUserId();
    
    const { error } = await supabase
      .from('attribution_events')
      .insert({
        user_id: userId,
        creator_id: data.creatorId,
        brand_id: data.brandId,
        event_type: data.eventType,
        path_type: data.pathType,
        transaction_value: data.transactionValue || null,
        offer_code_used: data.offerCodeUsed || null,
        offer_code_backed: data.offerCodeBacked || null
      });

    if (error) {
      console.error('[backrAI] Error logging attribution event:', error);
      // Don't throw - just log the error so it doesn't break the user flow
      // The error is likely due to invalid data format (UUID, etc.)
      if (error.code === '22P02') {
        console.error('[backrAI] UUID format error - user_id might be invalid:', userId);
      }
      return; // Don't throw, just return silently
    }
    
    console.log('[backrAI] Attribution event logged successfully');
  } catch (error) {
    console.error('[backrAI] Failed to log attribution event:', error);
    // Don't throw - just log so it doesn't break the user experience
    if (error instanceof Error) {
      console.error('[backrAI] Error details:', {
        message: error.message,
        name: error.name,
        stack: error.stack
      });
    }
  }
}

