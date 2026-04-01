-- 1. Enable the UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Create the sessions table
-- Using BIGINT for internal ID and UUID for grouping conversations
CREATE TABLE IF NOT EXISTS public.sessions (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    session_id UUID NOT NULL, 
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Add an index for faster history retrieval
CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON public.sessions (session_id);

-- 4. Enable RLS (Optional/Recommended)
ALTER TABLE public.sessions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow public access" ON public.sessions FOR ALL USING (true);
