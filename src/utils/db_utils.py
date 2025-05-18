import re

def postgresArrayToList(array):
    """
    Converts a PostgreSQL array to a string representation.

    params:
    - array: PostgreSQL array

    Returns:
    - string representation of the array
    """
    if not array:
        return []

    return array.strip("{}").split(",")

def get_schema_table_names(schema_file):
    """
    Extracts all table names from schema.sql file

    params:
    - path to schema.sql file

    Returns:
    - list of all table names as strings
    """
    try:
        with open(schema_file, "r") as f:
            schema_content = f.read()
        
        create_table_pattern = re.compile(r"CREATE TABLE IF NOT EXISTS\s+(\w+)", re.IGNORECASE)

        table_names = create_table_pattern.findall(schema_content)
        return table_names
    except FileNotFoundError:
        print(f"Error: The file '{schema_file}' was not found.")
        return []
    except Exception as e:
        print(f"Error: An unexpected error occurred extracting schema table names: {e}")
        return []

def all_tables_empty(conn):
    """
    Checks if database tables contain any data.

    params:
    - conn: database connection
    """
    print("Checking if existing db tables are empty")
    table_names = get_schema_table_names()
    try:
        with conn:
            with conn.cursor() as cur:
                for table in table_names:
                    cur.execute(f"SELECT EXISTS (SELECT 1 FROM {table} LIMIT 1);")
                    is_not_empty = cur.fetchone()[0]

                    if is_not_empty:
                        print("Existing db tables are populated.")
                        return False

                print("Existing db tables are all empty.")
                return True
    except Exception as e:
        print(f"Error occurred while checking tables: {e}")
        return False