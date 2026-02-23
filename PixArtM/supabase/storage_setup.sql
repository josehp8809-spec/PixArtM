-- ============================================================================
-- PixArtM — Supabase Storage Setup
-- Replaces: Firebase Storage + storage.rules
-- ============================================================================
-- Run this in the Supabase SQL Editor after creating the project.

-- Create 'photos' bucket (event photos)
INSERT INTO storage.buckets (id, name, public)
VALUES ('photos', 'photos', true)
ON CONFLICT (id) DO NOTHING;

-- Create 'zips' bucket (album ZIP archives)
INSERT INTO storage.buckets (id, name, public)
VALUES ('zips', 'zips', true)
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- Storage RLS Policies (replaces storage.rules)
-- ============================================================================

-- Anyone can READ photos (public bucket, but we still add policy)
CREATE POLICY "Public read photos"
    ON storage.objects FOR SELECT
    USING (bucket_id = 'photos');

-- Anyone can READ zips
CREATE POLICY "Public read zips"
    ON storage.objects FOR SELECT
    USING (bucket_id = 'zips');

-- Only service_role can UPLOAD (Edge Functions handle uploads)
-- No INSERT policy for anon = no public uploads
