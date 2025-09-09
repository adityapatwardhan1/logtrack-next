CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ,
    service TEXT,
    severity TEXT,
    message TEXT,
    "user" TEXT,
    extra_fields JSONB
);

CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    rule_id TEXT,
    triggered_at TIMESTAMPTZ NOT NULL,
    message TEXT NOT NULL,
    related_log_ids INTEGER[]
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS rules (
    id TEXT PRIMARY KEY,
    rule_type TEXT NOT NULL,
    service TEXT,
    keyword TEXT,
    message TEXT,
    threshold INTEGER,
    window_minutes INTEGER,
    window_seconds INTEGER,
    max_idle_minutes INTEGER,
    user_field TEXT,
    description TEXT,
    created_by INTEGER REFERENCES users(id)
);
