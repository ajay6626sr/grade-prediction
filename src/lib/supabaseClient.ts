import { createClient } from '@supabase/supabase-js'

// ⚠️ Replace these with your actual Supabase values
const supabaseUrl = "https://amuetmwaulcbtgazgjlc.supabase.co"
const supabaseAnonKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFtdWV0bXdhdWxjYnRnYXpnamxjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE3NjM0MDksImV4cCI6MjA3NzMzOTQwOX0.0IHwPWYVkeDvKfB7rwuo3hG19DkLSTEqrjaqhc_HOBE"

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

