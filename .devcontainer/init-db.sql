-- Initialize Oatie AI development database
-- This script sets up the basic database structure for development

-- Create application database if it doesn't exist
-- (This will run after the database is created by docker-compose)

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create application user with appropriate permissions
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'oatie_user') THEN
        CREATE USER oatie_user WITH PASSWORD 'oatie_password';
    END IF;
END
$$;

-- Grant permissions to application user
GRANT CONNECT ON DATABASE oatie_ai TO oatie_user;
GRANT USAGE ON SCHEMA public TO oatie_user;
GRANT CREATE ON SCHEMA public TO oatie_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO oatie_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO oatie_user;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO oatie_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO oatie_user;

-- Create development-specific configuration
INSERT INTO pg_settings (name, setting) VALUES ('log_statement', 'all') ON CONFLICT DO NOTHING;

-- Output setup confirmation
SELECT 'Oatie AI development database initialized successfully' AS status;