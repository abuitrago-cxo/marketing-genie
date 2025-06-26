-- Migration: Create user_identities table for storing external provider tokens
-- Provides GitHub OAuth token storage (and other providers in the future)

CREATE TABLE IF NOT EXISTS user_identities (
    user_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    access_token TEXT NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (user_id, provider)
);

-- Optional: quick lookup by provider
CREATE INDEX IF NOT EXISTS idx_user_identities_provider ON user_identities (provider);

-- Optional: lookup by user
CREATE INDEX IF NOT EXISTS idx_user_identities_user ON user_identities (user_id);
