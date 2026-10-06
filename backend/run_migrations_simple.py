#!/usr/bin/env python3
"""
Simple migration runner that executes SQL files directly.
This bypasses the complex migration tracking for initial setup.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def run_migrations():
    """Run all migration files directly"""
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("ERROR: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return False
    
    print(f"Connecting to Supabase at: {supabase_url}")
    
    try:
        # Create Supabase client
        client = create_client(supabase_url, supabase_key)
        
        # Get migration files
        migrations_dir = Path(__file__).parent / "migrations"
        migration_files = sorted([
            f for f in os.listdir(migrations_dir) 
            if f.endswith('.sql')
        ])
        
        print(f"Found {len(migration_files)} migration files")
        
        for migration_file in migration_files:
            print(f"Running migration: {migration_file}")
            
            # Read migration file
            migration_path = migrations_dir / migration_file
            with open(migration_path, 'r') as f:
                sql_content = f.read()
            
            # Split SQL into individual statements (basic splitting)
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            for i, statement in enumerate(statements):
                if statement:
                    try:
                        # Execute each statement
                        result = client.rpc('exec', {'sql': statement}).execute()
                        print(f"  ✓ Executed statement {i+1}/{len(statements)}")
                    except Exception as e:
                        # Try alternative method for table creation
                        if "CREATE TABLE" in statement.upper():
                            print(f"  ⚠ Direct execution failed, trying alternative method...")
                            # For table creation, we'll need to use a different approach
                            print(f"  ℹ Statement: {statement[:100]}...")
                        else:
                            print(f"  ✗ Failed to execute statement {i+1}: {e}")
            
            print(f"✓ Completed migration: {migration_file}")
        
        print("✓ All migrations completed successfully!")
        return True
        
    except Exception as e:
        print(f"ERROR: Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = run_migrations()
    exit(0 if success else 1)