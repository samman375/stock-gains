import os
import glob
import psycopg2
from pathlib import Path

def apply_migrations(conn):
    """
    Apply any pending database migrations.
    
    Migrations are SQL files stored in the migrations/ folder and are applied
    in alphabetical order. Each migration is tracked in the schema_migrations table
    to ensure it's only applied once.
    
    params:
    - conn: database connection
    """
    try:
        with conn.cursor() as cur:
            # Create migrations tracking table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id SERIAL PRIMARY KEY,
                    migration_name VARCHAR(255) UNIQUE NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            
            # Get the migrations directory path
            migrations_dir = Path(__file__).parent / "migrations"
            
            if not migrations_dir.exists():
                print("No migrations directory found.")
                return
            
            # Get list of migration files sorted by name
            migration_files = sorted(migrations_dir.glob("*.sql"))
            
            if not migration_files:
                print("No migrations to apply.")
                return
            
            print(f"Found {len(migration_files)} migration(s).")
            
            for migration_file in migration_files:
                migration_name = migration_file.name
                
                # Check if migration has already been applied
                cur.execute("SELECT 1 FROM schema_migrations WHERE migration_name = %s", (migration_name,))
                if cur.fetchone():
                    print(f"✓ Already applied: {migration_name}")
                    continue
                
                # Read and apply the migration
                try:
                    with open(migration_file, 'r') as f:
                        migration_sql = f.read()
                    
                    print(f"Applying migration: {migration_name}")
                    cur.execute(migration_sql)
                    
                    # Record the migration
                    cur.execute("INSERT INTO schema_migrations (migration_name) VALUES (%s)", (migration_name,))
                    conn.commit()
                    print(f"✓ Successfully applied: {migration_name}")
                    
                except Exception as e:
                    conn.rollback()
                    print(f"✗ Failed to apply migration {migration_name}: {e}")
                    raise
    
    except psycopg2.Error as e:
        print(f"Database error during migrations: {e}")
        raise
