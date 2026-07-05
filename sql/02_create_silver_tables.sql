CREATE TABLE IF NOT EXISTS silver.jobs_it (
    id SERIAL PRIMARY KEY,
    external_id TEXT,
    title TEXT,
    company TEXT,
    location TEXT,
    job_type TEXT,
    category TEXT,
    description TEXT,
    url TEXT,
    source TEXT,
    published_at TIMESTAMP,
    raw_file TEXT,
    processed_at TIMESTAMP,
    is_it_related BOOLEAN,
    skills TEXT,
    total_skills_detected INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS silver.job_skills (
    job_index INTEGER,
    external_id TEXT,
    source TEXT,
    url TEXT,
    skill_name TEXT
);

CREATE TABLE IF NOT EXISTS silver.skills_catalog (
    skill_name TEXT PRIMARY KEY
);
