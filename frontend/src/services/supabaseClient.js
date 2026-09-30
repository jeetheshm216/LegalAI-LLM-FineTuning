/**
 * supabaseClient.js
 * 
 * Supabase client configuration and initialization for LegalAI.
 * Formats project reference into a full Supabase URL if provided as an ID,
 * and initializes the Supabase client safely with session persistence.
 */

import { createClient } from '@supabase/supabase-js';

const env = (typeof import.meta !== 'undefined' && import.meta.env) || (typeof process !== 'undefined' && process.env) || {};
const rawUrl = env.VITE_SUPABASE_URL || '';
// Format project ref (e.g. 'brveublsqvbulxxkgjxu') to 'https://brveublsqvbulxxkgjxu.supabase.co'
const supabaseUrl = rawUrl.startsWith('http://') || rawUrl.startsWith('https://')
  ? rawUrl
  : (rawUrl ? `https://${rawUrl}.supabase.co` : '');

const supabaseAnonKey = env.VITE_SUPABASE_PUBLISHABLE_KEY || '';

export const isSupabaseConfigured = Boolean(supabaseUrl && supabaseAnonKey);

export const supabase = isSupabaseConfigured
  ? createClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: true,
      },
    })
  : null;

/**
 * Helper to check connection status to Supabase.
 */
export async function checkSupabaseConnection() {
  if (!supabase) {
    return { ok: false, error: 'Supabase client is not configured (missing URL or Key)' };
  }
  try {
    const { data, error } = await supabase.auth.getSession();
    if (error) return { ok: false, error: error.message };
    return { ok: true, session: data.session };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

export default supabase;
