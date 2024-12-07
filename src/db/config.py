import os

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "default_db": "postgres",
    "target_database": "stock-gains-store",
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "sslmode": "prefer"
}
