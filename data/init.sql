-- KnowledgeGlow Database Schema
-- SQLite database initialization script

-- Knowledge items table
CREATE TABLE IF NOT EXISTS knowledge_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source_type TEXT NOT NULL CHECK (source_type IN ('text', 'url', 'file')),
    source_url TEXT,
    tags TEXT, -- JSON array of tags
    summary TEXT,
    ai_analysis TEXT, -- AI-generated analysis
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- Tags table for better organization
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    color TEXT DEFAULT '#007bff',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Knowledge item tags relationship
CREATE TABLE IF NOT EXISTS knowledge_item_tags (
    knowledge_item_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY (knowledge_item_id, tag_id),
    FOREIGN KEY (knowledge_item_id) REFERENCES knowledge_items(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- Search history for analytics
CREATE TABLE IF NOT EXISTS search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    results_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- AI processing logs
CREATE TABLE IF NOT EXISTS ai_processing_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    knowledge_item_id INTEGER,
    processing_type TEXT NOT NULL, -- 'summary', 'analysis', 'tags'
    input_text TEXT,
    output_text TEXT,
    processing_time_ms INTEGER,
    status TEXT DEFAULT 'success', -- 'success', 'error', 'timeout'
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (knowledge_item_id) REFERENCES knowledge_items(id) ON DELETE CASCADE
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_knowledge_items_created_at ON knowledge_items(created_at);
CREATE INDEX IF NOT EXISTS idx_knowledge_items_source_type ON knowledge_items(source_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_items_is_active ON knowledge_items(is_active);
CREATE INDEX IF NOT EXISTS idx_search_history_created_at ON search_history(created_at);
CREATE INDEX IF NOT EXISTS idx_ai_processing_logs_created_at ON ai_processing_logs(created_at);

-- Insert sample data
INSERT OR IGNORE INTO tags (name, color) VALUES 
    ('AI', '#ff6b6b'),
    ('Technology', '#4ecdc4'),
    ('Research', '#45b7d1'),
    ('Development', '#96ceb4'),
    ('Documentation', '#feca57');

-- Sample knowledge items
INSERT OR IGNORE INTO knowledge_items (title, content, source_type, tags, summary) VALUES 
    ('AI Development Best Practices', 'Key principles for developing AI applications include proper data validation, model versioning, and ethical considerations.', 'text', '["AI", "Development"]', 'Guidelines for responsible AI development'),
    ('Machine Learning Fundamentals', 'Understanding supervised, unsupervised, and reinforcement learning approaches for different problem types.', 'text', '["AI", "Research"]', 'Overview of core ML concepts'),
    ('Database Design Principles', 'Normalization, indexing, and query optimization techniques for efficient database systems.', 'text', '["Technology", "Development"]', 'Essential database design concepts');