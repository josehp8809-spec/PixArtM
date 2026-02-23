-- PixArtM Desktop App Database Schema
-- SQLite database for local project management

-- ============================================================================
-- PROJECTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS projects (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  plan TEXT NOT NULL CHECK(plan IN ('free', 'basic', 'pro', 'premium')),
  photo_limit INTEGER NOT NULL,
  validity_days INTEGER NOT NULL,
  has_cloud_album INTEGER NOT NULL, -- 0 = false, 1 = true
  start_date TEXT NOT NULL, -- ISO 8601
  end_date TEXT NOT NULL,   -- ISO 8601
  status TEXT NOT NULL DEFAULT 'draft' CHECK(status IN ('draft', 'active', 'expired', 'cleaned')),
  frame_design TEXT,  -- JSON serialized FrameDesign
  gallery_token TEXT UNIQUE NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  deployed_at TEXT
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at DESC);

-- ============================================================================
-- EXPORT HISTORY TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS export_history (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  export_type TEXT NOT NULL CHECK(export_type IN ('png', 'svg', 'pdf')),
  qr_settings TEXT NOT NULL,  -- JSON serialized QRSettings
  exported_at TEXT NOT NULL,
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_export_history_project_id ON export_history(project_id);
CREATE INDEX IF NOT EXISTS idx_export_history_exported_at ON export_history(exported_at DESC);

-- ============================================================================
-- QR SETTINGS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS qr_settings (
  project_id TEXT PRIMARY KEY,
  dark_color TEXT NOT NULL DEFAULT '#000000',
  light_color TEXT NOT NULL DEFAULT '#FFFFFF',
  has_gradient INTEGER NOT NULL DEFAULT 0,
  gradient_colors TEXT,  -- JSON array of colors
  logo_url TEXT,
  error_correction TEXT NOT NULL DEFAULT 'M' CHECK(error_correction IN ('L', 'M', 'Q', 'H')),
  corner_style TEXT NOT NULL DEFAULT 'square' CHECK(corner_style IN ('square', 'rounded')),
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- ============================================================================
-- APP SETTINGS TABLE (for Firebase credentials, Gemini API key, etc.)
-- ============================================================================
CREATE TABLE IF NOT EXISTS app_settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
