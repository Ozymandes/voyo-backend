-- Conversation memory table for CLEO chat history
-- Run this in Supabase SQL Editor

CREATE TABLE IF NOT EXISTS public.conversation_messages (
    id          BIGSERIAL PRIMARY KEY,
    user_id     UUID        NOT NULL,
    role        TEXT        NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content     TEXT        NOT NULL,
    metadata    JSONB       NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conv_messages_user_created
    ON public.conversation_messages (user_id, created_at);

ALTER TABLE public.conversation_messages ENABLE ROW LEVEL SECURITY;

-- Service role (used by the backend) can do everything
CREATE POLICY "service_full_access" ON public.conversation_messages
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Authenticated users can only see their own messages
CREATE POLICY "users_own_messages" ON public.conversation_messages
    FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());
