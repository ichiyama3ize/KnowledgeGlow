#!/usr/bin/env python3
"""
Database management for KnowledgeGlow AI Service
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Any

DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/knowledge.db")

def get_db_connection():
    """Get database connection with proper configuration"""
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn

def init_database():
    """Initialize database with schema"""
    try:
        # Read and execute schema
        schema_path = os.path.join(os.path.dirname(DATABASE_PATH), "init.sql")
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema = f.read()
            
            conn = get_db_connection()
            conn.executescript(schema)
            conn.commit()
            conn.close()
            print(f"✅ Database initialized at {DATABASE_PATH}")
        else:
            # Create basic schema if init.sql doesn't exist
            create_basic_schema()
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

def create_basic_schema():
    """Create basic database schema"""
    conn = get_db_connection()
    
    # Knowledge items table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            source_type TEXT NOT NULL CHECK (source_type IN ('text', 'url', 'file')),
            source_url TEXT,
            tags TEXT,
            summary TEXT,
            ai_analysis TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # AI processing logs
    conn.execute('''
        CREATE TABLE IF NOT EXISTS ai_processing_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            knowledge_item_id INTEGER,
            processing_type TEXT NOT NULL,
            input_text TEXT,
            output_text TEXT,
            processing_time_ms INTEGER,
            status TEXT DEFAULT 'success',
            error_message TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (knowledge_item_id) REFERENCES knowledge_items(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

class KnowledgeDB:
    """Database operations for knowledge management"""
    
    @staticmethod
    def create_knowledge_item(title: str, content: str, source_type: str, 
                            source_url: str = None, tags: List[str] = None,
                            summary: str = None, ai_analysis: str = None) -> int:
        """Create a new knowledge item"""
        conn = get_db_connection()
        
        tags_json = json.dumps(tags) if tags else None
        
        cursor = conn.execute('''
            INSERT INTO knowledge_items 
            (title, content, source_type, source_url, tags, summary, ai_analysis)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, content, source_type, source_url, tags_json, summary, ai_analysis))
        
        item_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return item_id
    
    @staticmethod
    def get_knowledge_item(item_id: int) -> Optional[Dict[str, Any]]:
        """Get a knowledge item by ID"""
        conn = get_db_connection()
        
        row = conn.execute('''
            SELECT * FROM knowledge_items WHERE id = ? AND is_active = 1
        ''', (item_id,)).fetchone()
        
        conn.close()
        
        if row:
            item = dict(row)
            if item['tags']:
                item['tags'] = json.loads(item['tags'])
            return item
        return None
    
    @staticmethod
    def get_all_knowledge_items(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all knowledge items with pagination"""
        conn = get_db_connection()
        
        rows = conn.execute('''
            SELECT * FROM knowledge_items 
            WHERE is_active = 1 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset)).fetchall()
        
        conn.close()
        
        items = []
        for row in rows:
            item = dict(row)
            if item['tags']:
                item['tags'] = json.loads(item['tags'])
            items.append(item)
        
        return items
    
    @staticmethod
    def update_knowledge_item(item_id: int, **kwargs) -> bool:
        """Update a knowledge item"""
        if not kwargs:
            return False
        
        # Handle tags serialization
        if 'tags' in kwargs and isinstance(kwargs['tags'], list):
            kwargs['tags'] = json.dumps(kwargs['tags'])
        
        # Build dynamic update query
        set_clauses = []
        values = []
        
        for key, value in kwargs.items():
            if key in ['title', 'content', 'source_url', 'tags', 'summary', 'ai_analysis']:
                set_clauses.append(f"{key} = ?")
                values.append(value)
        
        if not set_clauses:
            return False
        
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        values.append(item_id)
        
        query = f'''
            UPDATE knowledge_items 
            SET {', '.join(set_clauses)}
            WHERE id = ? AND is_active = 1
        '''
        
        conn = get_db_connection()
        cursor = conn.execute(query, values)
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0
    
    @staticmethod
    def delete_knowledge_item(item_id: int) -> bool:
        """Soft delete a knowledge item"""
        conn = get_db_connection()
        
        cursor = conn.execute('''
            UPDATE knowledge_items 
            SET is_active = 0, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND is_active = 1
        ''', (item_id,))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0
    
    @staticmethod
    def search_knowledge_items(query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search knowledge items by content"""
        conn = get_db_connection()
        
        search_term = f"%{query}%"
        rows = conn.execute('''
            SELECT * FROM knowledge_items 
            WHERE is_active = 1 
            AND (title LIKE ? OR content LIKE ? OR summary LIKE ?)
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (search_term, search_term, search_term, limit)).fetchall()
        
        conn.close()
        
        items = []
        for row in rows:
            item = dict(row)
            if item['tags']:
                item['tags'] = json.loads(item['tags'])
            items.append(item)
        
        return items
    
    @staticmethod
    def log_ai_processing(knowledge_item_id: int, processing_type: str,
                         input_text: str, output_text: str, processing_time_ms: int,
                         status: str = 'success', error_message: str = None) -> int:
        """Log AI processing activity"""
        conn = get_db_connection()
        
        cursor = conn.execute('''
            INSERT INTO ai_processing_logs 
            (knowledge_item_id, processing_type, input_text, output_text, 
             processing_time_ms, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (knowledge_item_id, processing_type, input_text, output_text,
              processing_time_ms, status, error_message))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return log_id