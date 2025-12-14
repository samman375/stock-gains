import sys
import psycopg2
from psycopg2 import OperationalError

from db.config import DB_CONFIG, TABLE_SCHEMA_FILE
from db.backup_handler import restore_database, get_latest_backup

def get_connection(default_db=False):
    """
    Get db connection. Returns connection to target db by default.
    
    params:
    - default_db: Returns default db connection if set to true.
    """
    try:
        return psycopg2.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            database=DB_CONFIG["default_db"] if default_db else DB_CONFIG["target_db"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
    except OperationalError as e:
        print("Error: Could not connect to the PostgreSQL server. Ensure postgresql is installed and running.")
        print(f"Details: {e}")
        sys.exit(1)

def target_database_exists(default_conn):
    """
    Checks if target db exists in default db

    params:
    - default_conn: default database connection
    """
    print("Checking if database exists...")
    with default_conn.cursor() as cur:
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_CONFIG['target_db']}'")
        exists = cur.fetchone() is not None

    print("Database exists." if exists else "Database does not exist.")
    return exists

def create_database(default_conn):
    """
    Creates target database.

    params:
    - default_conn: default database connection
    """
    print("Creating database...")
    db_name = DB_CONFIG["target_db"]

    with default_conn.cursor() as cur:
        cur.execute(f"CREATE DATABASE {db_name}")
        print(f"Database '{db_name}' created.")

def tables_have_data(conn):
    """
    Checks if database tables have any data

    params:
    - conn: database connection
    
    Returns:
    - bool: True if any tables have data, False otherwise
    """
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM investment_history LIMIT 1")
            has_data = cur.fetchone() is not None
        return has_data
    except Exception as e:
        return False

def setup_tables(conn):
    """
    Creates tables from schema file

    params:
    - conn: database connection
    """
    print("Creating database tables if don't already exist...")
    try:
        with conn:
            with conn.cursor() as cur:
                with open(TABLE_SCHEMA_FILE, "r") as f:
                    schema_sql = f.read()
                cur.execute(schema_sql)
                print("Successfully created tables.")
    except Exception as e:
        print(f"Error setting up tables: {e}")
        sys.exit(1)

def database_setup():
    """
    Sets up database if not already created.
    Also creates tables if not already created.
    If tables are empty, attempts to restore from backup.

    Returns:
    - conn: database connection.
    """
    default_conn = get_connection(default_db=True)

    if not default_conn:
        return None

    # Disable transaction block since db cant be created in one
    default_conn.autocommit = True

    if not target_database_exists(default_conn):
        create_database(default_conn)

    default_conn.close()

    conn = get_connection()

    if conn:
        if not tables_have_data(conn):
            # Tables are empty, try to restore from backup
            latest_backup = get_latest_backup()
            if latest_backup:
                print("No data found in database. Restoring from latest backup...")
                # Close the connection before restoring
                conn.close()
                try:
                    restore_success = restore_database()
                    if restore_success:
                        print("Database successfully restored from backup.")
                        # Reconnect after restore completes
                        conn = get_connection()
                    else:
                        print("Failed to restore from backup.")
                        print("Creating empty database schema instead.")
                        conn = get_connection()
                        setup_tables(conn)
                except Exception as e:
                    print(f"Failed to restore from backup: {e}")
                    print("Creating empty database schema instead.")
                    conn = get_connection()
                    setup_tables(conn)
            else:
                print("No backups found. Creating empty database schema.")
                setup_tables(conn)
        else:
            print("Database already contains data.")

    return conn
