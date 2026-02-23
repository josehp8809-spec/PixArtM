-- ============================================================================
-- PixArtM — Supabase Schema
-- Replaces: Firestore collections (events, captures) + firestore.rules
-- ============================================================================

-- EVENTS table (replaces Firestore 'events' collection)
CREATE TABLE IF NOT EXISTS events (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug        TEXT UNIQUE NOT NULL,
    name        TEXT NOT NULL,
    plan        TEXT NOT NULL CHECK (plan IN ('free','basic','pro','premium')),

    -- Limits
    photo_limit     INT NOT NULL DEFAULT 10,
    validity_days   INT NOT NULL DEFAULT 3,
    has_cloud_album BOOLEAN NOT NULL DEFAULT FALSE,

    -- Scheduling
    start_date  TIMESTAMPTZ NOT NULL,
    end_date    TIMESTAMPTZ NOT NULL,

    -- Status
    status          TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','active','expired','cleaned')),
    capture_count   INT NOT NULL DEFAULT 0,
    reserved_count  INT NOT NULL DEFAULT 0,

    -- Frame design (JSON blob, same as Firestore)
    frame_design    JSONB,

    -- Gallery
    gallery_token       TEXT NOT NULL DEFAULT encode(gen_random_bytes(16), 'hex'),
    gallery_expires_at  TIMESTAMPTZ,

    -- Analytics (JSON, lightweight)
    analytics   JSONB DEFAULT '{"totalCaptures":0}'::jsonb,

    -- Metadata
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    deployed_at TIMESTAMPTZ
);

-- Index for slug lookups (Camera page uses slug)
CREATE INDEX IF NOT EXISTS idx_events_slug ON events (slug);
-- Index for status-based queries (cleanup, gallery)
CREATE INDEX IF NOT EXISTS idx_events_status ON events (status);


-- CAPTURES table (replaces Firestore subcollection 'events/{id}/captures')
CREATE TABLE IF NOT EXISTS captures (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id        UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    capture_number  INT NOT NULL,
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT now(),
    storage_url     TEXT,
    storage_path    TEXT,
    device_saved    BOOLEAN NOT NULL DEFAULT FALSE,
    uploaded_to_cloud BOOLEAN NOT NULL DEFAULT FALSE,

    -- Image metadata
    original_size    INT,
    compressed_size  INT,
    width            INT,
    height           INT
);

-- Index for gallery queries (cloud photos ordered by capture number)
CREATE INDEX IF NOT EXISTS idx_captures_event ON captures (event_id, capture_number);
CREATE INDEX IF NOT EXISTS idx_captures_cloud ON captures (event_id, uploaded_to_cloud);


-- CLEANUP LOGS table (replaces Firestore 'cleanup_logs' collection)
CREATE TABLE IF NOT EXISTS cleanup_logs (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp               TIMESTAMPTZ NOT NULL DEFAULT now(),
    events_processed        INT DEFAULT 0,
    events_cleaned_success  INT DEFAULT 0,
    events_cleaned_failed   INT DEFAULT 0,
    total_photos_deleted    INT DEFAULT 0,
    total_zips_deleted      INT DEFAULT 0
);


-- CLEANUP ERRORS table
CREATE TABLE IF NOT EXISTS cleanup_errors (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id    UUID REFERENCES events(id),
    event_name  TEXT,
    error       TEXT,
    fatal       BOOLEAN DEFAULT FALSE,
    timestamp   TIMESTAMPTZ NOT NULL DEFAULT now()
);


-- ============================================================================
-- ROW LEVEL SECURITY (replaces firestore.rules)
-- ============================================================================

ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE captures ENABLE ROW LEVEL SECURITY;
ALTER TABLE cleanup_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE cleanup_errors ENABLE ROW LEVEL SECURITY;

-- Public can READ active & expired events (same as Firestore rule)
CREATE POLICY "Public read active/expired events"
    ON events FOR SELECT
    USING (status IN ('active', 'expired'));

-- Public can READ captures of active/expired events
CREATE POLICY "Public read captures of active events"
    ON captures FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM events
            WHERE events.id = captures.event_id
            AND events.status IN ('active', 'expired')
        )
    );

-- Service role (Edge Functions / Admin) can do everything
-- (service_role key bypasses RLS automatically in Supabase)

-- No public INSERT/UPDATE/DELETE policies = clients cannot write
-- All writes go through Edge Functions using service_role key


-- ============================================================================
-- AUTO-UPDATE updated_at trigger
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER events_updated_at
    BEFORE UPDATE ON events
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
