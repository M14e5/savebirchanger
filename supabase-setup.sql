-- Supabase Setup for Canvassing Planner
-- Run this SQL in your Supabase SQL Editor (https://jwbjrgpcwwqrumstaqfi.supabase.co)

-- 1. Create the roads table
CREATE TABLE IF NOT EXISTS roads (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    geojson JSONB NOT NULL,
    last_checked DATE,
    status TEXT DEFAULT 'none' CHECK (status IN ('none', 'todo', 'doing', 'done')),
    updated_by TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Create index for faster searches
CREATE INDEX IF NOT EXISTS idx_roads_name ON roads USING gin(to_tsvector('english', name));
CREATE INDEX IF NOT EXISTS idx_roads_status ON roads (status);
CREATE INDEX IF NOT EXISTS idx_roads_last_checked ON roads (last_checked);

-- 3. Enable Row Level Security (RLS) but allow public access for MVP
ALTER TABLE roads ENABLE ROW LEVEL SECURITY;

-- 4. Create policy to allow anonymous read/write (for MVP - tighten later)
CREATE POLICY "Allow anonymous access" ON roads
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- 5. Create a function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 6. Create trigger to auto-update timestamp
DROP TRIGGER IF EXISTS update_roads_updated_at ON roads;
CREATE TRIGGER update_roads_updated_at
    BEFORE UPDATE ON roads
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Verify table was created
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'roads';
