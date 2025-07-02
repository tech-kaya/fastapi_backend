#!/usr/bin/env python3
"""
Database Schema Checker
This script checks the current database schema and compares it with expected structure
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings
from loguru import logger


async def check_database_connection():
    """Test basic database connection"""
    try:
        engine = create_async_engine(settings.database_url)
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            logger.info(f"✅ Database connection successful!")
            logger.info(f"📊 PostgreSQL version: {version}")
            return engine
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        return None


async def list_all_tables(engine):
    """List all tables in the database"""
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = result.fetchall()
            
            logger.info(f"📋 Found {len(tables)} tables in database:")
            for table in tables:
                logger.info(f"  - {table[0]}")
            
            return [table[0] for table in tables]
    except Exception as e:
        logger.error(f"❌ Error listing tables: {str(e)}")
        return []


async def check_table_schema(engine, table_name):
    """Check the schema of a specific table"""
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text(f"""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                AND table_schema = 'public'
                ORDER BY ordinal_position
            """))
            columns = result.fetchall()
            
            logger.info(f"🔍 Schema for table '{table_name}':")
            if not columns:
                logger.warning(f"   ⚠️  Table '{table_name}' not found or has no columns")
                return []
            
            for col in columns:
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                default = f"DEFAULT {col[3]}" if col[3] else ""
                logger.info(f"   📌 {col[0]} | {col[1]} | {nullable} {default}")
            
            return columns
    except Exception as e:
        logger.error(f"❌ Error checking table schema for {table_name}: {str(e)}")
        return []


async def check_expected_tables(engine):
    """Check if our expected tables exist with correct structure"""
    
    expected_tables = {
        'places': ['id', 'name', 'website_url'],
        'users': ['id', 'name', 'email', 'phone', 'message'],
        'form_submission': ['id', 'place_id', 'user_id', 'website_url', 'submission_status', 'error_message', 'submitted_at']
    }
    
    logger.info("🎯 Checking expected table structure...")
    
    for table_name, expected_columns in expected_tables.items():
        logger.info(f"\n📊 Checking table: {table_name}")
        
        # Check if table exists
        async with engine.begin() as conn:
            result = await conn.execute(text(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = '{table_name}'
                )
            """))
            table_exists = result.scalar()
        
        if not table_exists:
            logger.error(f"   ❌ Table '{table_name}' does not exist!")
            continue
        
        logger.info(f"   ✅ Table '{table_name}' exists")
        
        # Check columns
        columns = await check_table_schema(engine, table_name)
        existing_columns = [col[0] for col in columns]
        
        missing_columns = set(expected_columns) - set(existing_columns)
        extra_columns = set(existing_columns) - set(expected_columns)
        
        if missing_columns:
            logger.error(f"   ❌ Missing columns: {', '.join(missing_columns)}")
        if extra_columns:
            logger.warning(f"   ⚠️  Extra columns: {', '.join(extra_columns)}")
        if not missing_columns and not extra_columns:
            logger.info(f"   ✅ All expected columns present")


async def suggest_fixes(engine):
    """Suggest SQL commands to fix missing tables/columns"""
    
    logger.info("\n🔧 Suggested fixes:")
    
    # Check if tables exist
    tables = await list_all_tables(engine)
    
    if 'places' not in tables:
        logger.info("📝 Create places table:")
        logger.info("""
CREATE TABLE places (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    website_url VARCHAR(500) NOT NULL
);
""")
    
    if 'users' not in tables:
        logger.info("📝 Create users table:")
        logger.info("""
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    message TEXT
);
""")
    
    if 'form_submission' not in tables:
        logger.info("📝 Create form_submission table:")
        logger.info("""
CREATE TABLE form_submission (
    id SERIAL PRIMARY KEY,
    place_id INTEGER NOT NULL REFERENCES places(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    website_url VARCHAR(500) NOT NULL,
    submission_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    error_message TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")
    
    # Check for missing columns in existing tables
    if 'places' in tables:
        places_columns = await check_table_schema(engine, 'places')
        existing_cols = [col[0] for col in places_columns]
        
        if 'website_url' not in existing_cols:
            logger.info("📝 Add missing website_url column to places:")
            logger.info("ALTER TABLE places ADD COLUMN website_url VARCHAR(500);")


async def insert_sample_data(engine):
    """Insert sample data for testing"""
    
    logger.info("\n🔄 Sample data commands:")
    logger.info("""
-- Insert sample places
INSERT INTO places (name, website_url) VALUES 
('Example Company 1', 'https://example1.com'),
('Example Company 2', 'https://example2.com'),
('Test Business', 'https://testbusiness.com');

-- Insert sample users  
INSERT INTO users (name, email, phone, message) VALUES 
('John Doe', 'john@example.com', '+1234567890', 'Hello, I am interested in your services.'),
('Jane Smith', 'jane@example.com', '+0987654321', 'Please contact me about your products.');
""")


async def main():
    """Main function to run all database checks"""
    
    logger.info("🚀 Starting Database Schema Check")
    logger.info("=" * 50)
    
    # Test connection
    engine = await check_database_connection()
    if not engine:
        logger.error("Cannot proceed without database connection")
        return
    
    # List all tables
    logger.info("\n" + "=" * 50)
    tables = await list_all_tables(engine)
    
    # Check each table schema
    logger.info("\n" + "=" * 50)
    for table in tables:
        await check_table_schema(engine, table)
        logger.info("")
    
    # Check expected structure
    logger.info("=" * 50)
    await check_expected_tables(engine)
    
    # Suggest fixes
    logger.info("=" * 50)
    await suggest_fixes(engine)
    
    # Sample data
    logger.info("=" * 50)
    await insert_sample_data(engine)
    
    await engine.dispose()
    logger.info("\n✅ Database check completed!")


if __name__ == "__main__":
    asyncio.run(main())
