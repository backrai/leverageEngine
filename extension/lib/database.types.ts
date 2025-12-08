// Auto-generated types from Supabase
// Run: npx supabase gen types typescript --project-id YOUR_PROJECT_ID > lib/database.types.ts

export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[];

export interface Database {
  public: {
    Tables: {
      brands: {
        Row: {
          id: string;
          name: string;
          domain_pattern: string;
          logo_url: string | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          name: string;
          domain_pattern: string;
          logo_url?: string | null;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          name?: string;
          domain_pattern?: string;
          logo_url?: string | null;
          created_at?: string;
          updated_at?: string;
        };
      };
      creators: {
        Row: {
          id: string;
          display_name: string;
          avatar_url: string | null;
          email: string | null;
          affiliate_ref_code: string;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          display_name: string;
          avatar_url?: string | null;
          email?: string | null;
          affiliate_ref_code: string;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          display_name?: string;
          avatar_url?: string | null;
          email?: string | null;
          affiliate_ref_code?: string;
          created_at?: string;
          updated_at?: string;
        };
      };
      offers: {
        Row: {
          id: string;
          creator_id: string;
          brand_id: string;
          code: string;
          discount_amount: string;
          discount_type: string;
          is_active: boolean;
          expires_at: string | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          creator_id: string;
          brand_id: string;
          code: string;
          discount_amount: string;
          discount_type?: string;
          expires_at?: string | null;
          is_active?: boolean;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          creator_id?: string;
          brand_id?: string;
          code?: string;
          discount_amount?: string;
          discount_type?: string;
          expires_at?: string | null;
          is_active?: boolean;
          created_at?: string;
          updated_at?: string;
        };
      };
      attribution_events: {
        Row: {
          id: string;
          user_id: string | null;
          creator_id: string | null;
          brand_id: string | null;
          event_type: string;
          path_type: string;
          transaction_value: number | null;
          offer_code_used: string | null;
          offer_code_backed: string | null;
          created_at: string;
        };
        Insert: {
          id?: string;
          user_id?: string | null;
          creator_id?: string | null;
          brand_id?: string | null;
          event_type: string;
          path_type: string;
          transaction_value?: number | null;
          offer_code_used?: string | null;
          offer_code_backed?: string | null;
          created_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string | null;
          creator_id?: string | null;
          brand_id?: string | null;
          event_type?: string;
          path_type?: string;
          transaction_value?: number | null;
          offer_code_used?: string | null;
          offer_code_backed?: string | null;
          created_at?: string;
        };
      };
    };
  };
}

