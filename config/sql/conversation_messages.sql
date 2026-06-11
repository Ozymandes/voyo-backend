-- VOYO — conversation_messages table
-- Required by Phase 1B: CLEO persistent conversation memory.
-- Run this migration against your Supabase database before starting CLEO.

CREATE TABLE IF NOT EXISTS conversation_messages (
    id         BIGSERIAL   PRIMARY KEY,
    user_id    UUID        NOT NULL,
    role       VARCHAR(10) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content    TEXT        NOT NULL,
    metadata   JSONB       DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Fast lookup of recent messages per user (CLEO's primary read pattern)
CREATE INDEX IF NOT EXISTS idx_conv_msgs_user_created
    ON conversation_messages (user_id, created_at DESC);

-- Row-Level Security: users can only read their own messages
ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own messages"
    ON conversation_messages
    FOR SELECT
    USING (auth.uid() = user_id);

-- Service role bypasses RLS — CLEO uses the admin client for reads/writes
-- (no additional policy needed; service key ignores RLS by default)
