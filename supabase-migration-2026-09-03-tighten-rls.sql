-- Migration: tighten anonymous access to the canvassing `roads` table
-- Run once in the Supabase SQL editor: https://jwbjrgpcwwqrumstaqfi.supabase.co
--
-- WHY
-- The original policy was:
--     CREATE POLICY "Allow anonymous access" ON roads
--         FOR ALL USING (true) WITH CHECK (true);
-- commented "for MVP - tighten later".
--
-- The anon key that satisfies that policy is embedded in heatmap.html,
-- import_roads.html and import_roads.py, all of which are in a public
-- repository and served from the live site. Anon keys are designed to be
-- public, so the key is not the problem - the policy is. As written, anyone
-- who viewed the page source could insert or delete rows in this table, not
-- just read it and tick roads off.
--
-- AFTER THIS MIGRATION
--   anon may SELECT every row
--   anon may UPDATE only status, last_checked, updated_by, updated_at
--   anon may not INSERT or DELETE
--   seeding still works: import_roads.py uses the service_role key, which
--   bypasses RLS entirely
--
-- Safe to re-run.

BEGIN;

-- 1. Replace the blanket policy with two narrow ones.
DROP POLICY IF EXISTS "Allow anonymous access" ON roads;
DROP POLICY IF EXISTS "Anon can read roads" ON roads;
DROP POLICY IF EXISTS "Anon can update canvassing progress" ON roads;

CREATE POLICY "Anon can read roads" ON roads
    FOR SELECT
    USING (true);

CREATE POLICY "Anon can update canvassing progress" ON roads
    FOR UPDATE
    USING (true)
    WITH CHECK (true);

-- 2. A policy cannot limit which columns a role writes; GRANTs do that.
REVOKE ALL ON roads FROM anon;
GRANT SELECT ON roads TO anon;
GRANT UPDATE (status, last_checked, updated_by, updated_at) ON roads TO anon;

COMMIT;

-- 3. Verify. Expect: SELECT for anon on all columns, UPDATE on exactly the
--    four progress columns, and no INSERT or DELETE row anywhere.
SELECT privilege_type, column_name
FROM information_schema.column_privileges
WHERE grantee = 'anon' AND table_name = 'roads'
ORDER BY privilege_type, column_name;

-- And the policies that now exist on the table.
SELECT policyname, cmd, qual, with_check
FROM pg_policies
WHERE tablename = 'roads'
ORDER BY policyname;
