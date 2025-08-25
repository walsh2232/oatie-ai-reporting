-- PostgreSQL initialization script for Oatie AI Reporting
-- This script sets up the database with proper extensions and initial configuration

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create database if it doesn't exist (this runs after DB creation in initdb)
-- The database is already created by POSTGRES_DB env var

-- Set timezone
SET timezone = 'UTC';

-- Create application user with limited privileges (if needed for specific scenarios)
-- Note: The main user is already created via POSTGRES_USER env var

-- Performance tuning settings
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET track_activity_query_size = 2048;
ALTER SYSTEM SET log_min_duration_statement = 1000;
ALTER SYSTEM SET log_statement = 'mod';

-- Restart required for some settings to take effect
-- SELECT pg_reload_conf();

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO oatie;
GRANT CREATE ON SCHEMA public TO oatie;

-- Create initial tables will be handled by Alembic migrations
-- This script just sets up the database environment

COMMENT ON DATABASE oatie_ai IS 'Oatie AI Reporting Platform Database';

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Oatie AI database initialized successfully at %', NOW();
END $$;