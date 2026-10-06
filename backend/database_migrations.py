"""
Database migration utilities for Supabase.
Handles running SQL migrations and schema updates.
"""

import os
import logging
from pathlib import Path
from supabase import Client
from database import db

logger = logging.getLogger(__name__)

class MigrationManager:
    """Manages database migrations for the application"""
    
    def __init__(self, client: Client):
        self.client = client
        self.migrations_dir = Path(__file__).parent / "migrations"
    
    def run_migrations(self) -> bool:
        """Run all pending migrations"""
        try:
            # Create migrations tracking table if it doesn't exist
            self._create_migrations_table()
            
            # Get list of migration files
            migration_files = sorted([
                f for f in os.listdir(self.migrations_dir) 
                if f.endswith('.sql')
            ])
            
            for migration_file in migration_files:
                if not self._is_migration_applied(migration_file):
                    self._run_migration(migration_file)
                    logger.info(f"Applied migration: {migration_file}")
                else:
                    logger.info(f"Migration already applied: {migration_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    def _create_migrations_table(self):
        """Create table to track applied migrations"""
        sql = """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id SERIAL PRIMARY KEY,
            migration_name VARCHAR(255) UNIQUE NOT NULL,
            applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        self.client.rpc('exec_sql', {'sql': sql}).execute()
    
    def _is_migration_applied(self, migration_name: str) -> bool:
        """Check if a migration has already been applied"""
        try:
            result = self.client.table('schema_migrations')\
                .select('migration_name')\
                .eq('migration_name', migration_name)\
                .execute()
            return len(result.data) > 0
        except:
            return False
    
    def _run_migration(self, migration_file: str):
        """Run a single migration file"""
        migration_path = self.migrations_dir / migration_file
        
        with open(migration_path, 'r') as f:
            sql_content = f.read()
        
        # Execute the migration SQL
        self.client.rpc('exec_sql', {'sql': sql_content}).execute()
        
        # Record that migration was applied
        self.client.table('schema_migrations').insert({
            'migration_name': migration_file
        }).execute()

def run_database_migrations():
    """Run all database migrations"""
    try:
        client = db.get_client()
        migration_manager = MigrationManager(client)
        success = migration_manager.run_migrations()
        
        if success:
            logger.info("All migrations completed successfully")
        else:
            logger.error("Migration process failed")
            
        return success
        
    except Exception as e:
        logger.error(f"Failed to run migrations: {e}")
        return False

if __name__ == "__main__":
    # Run migrations when script is executed directly
    logging.basicConfig(level=logging.INFO)
    run_database_migrations()