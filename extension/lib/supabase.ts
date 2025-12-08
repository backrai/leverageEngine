import { createClient } from "@supabase/supabase-js";
import type { Database } from "./database.types";

// Plasmo requires PLASMO_PUBLIC_ prefix for environment variables
const supabaseUrl = process.env.PLASMO_PUBLIC_SUPABASE_URL || "";
const supabaseAnonKey = process.env.PLASMO_PUBLIC_SUPABASE_ANON_KEY || "";

if (!supabaseUrl || !supabaseAnonKey) {
  console.error("Missing Supabase environment variables. Please check your .env file.");
  throw new Error("Missing Supabase environment variables");
}

export const supabase = createClient<Database>(supabaseUrl, supabaseAnonKey);

