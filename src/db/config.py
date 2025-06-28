import os

current_dir = os.path.dirname(os.path.abspath(__file__))

TABLE_SCHEMA_FILE_NAME = "schema.sql"
TABLE_SCHEMA_FILE = os.path.join(current_dir, TABLE_SCHEMA_FILE_NAME)

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "default_db": "postgres",
    "target_db": "stock_gains_store",
    "user": os.getenv("PGUSER"),
    "password": os.getenv("PGPASSWORD"),
    "sslmode": "prefer"
}

BACKUP_DIRECTORY_CONFIG_NAME = "backup_path.json"
BACKUP_DIRECTORY_CONFIG = os.path.join(current_dir, BACKUP_DIRECTORY_CONFIG_NAME)
BACKUP_PREFIX = "stock-gains-db_"
BACKUP_DATETIME_STRF = "%Y%m%d%H%M%S"
BACKUP_EXTENSION = '.backup'
DEFAULT_BACKUPS_NUM = 3
