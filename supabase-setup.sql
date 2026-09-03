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

-- 3. Enable Row Level Security (RLS)
ALTER TABLE roads ENABLE ROW LEVEL SECURITY;

-- 4. Anonymous access: read the roads, and update canvassing progress on roads
--    that already exist. Nothing more.
--
--    The anon key is embedded in heatmap.html, which is served from a public
--    repository, so treat anon as "anyone on the internet". A single
--    FOR ALL / USING (true) / WITH CHECK (true) policy therefore let anyone
--    insert or delete rows in this table.
--
--    RLS policies cannot restrict which *columns* a role may write, so the
--    column list is enforced with GRANTs below. Together: anon may read
--    everything, may change only the four progress columns, and may not add or
--    remove roads. Seeding is done by import_roads.py with the service_role
--    key, which bypasses RLS.
DROP POLICY IF EXISTS "Allow anonymous access" ON roads;

CREATE POLICY "Anon can read roads" ON roads
    FOR SELECT
    USING (true);

CREATE POLICY "Anon can update canvassing progress" ON roads
    FOR UPDATE
    USING (true)
    WITH CHECK (true);

REVOKE ALL ON roads FROM anon;
GRANT SELECT ON roads TO anon;
GRANT UPDATE (status, last_checked, updated_by, updated_at) ON roads TO anon;

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
