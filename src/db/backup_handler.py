import os
import json
import subprocess
from datetime import datetime

from db.config import (
    DB_CONFIG,
    BACKUP_DIRECTORY_CONFIG, 
    BACKUP_PREFIX,
    BACKUP_DATETIME_STRF,
    BACKUP_EXTENSION,
    DEFAULT_BACKUPS_NUM     # TODO: Make this configurable
)

def is_valid_backup_location(dir_path):
    """
    Checks if directory exists, is writable, and is directory

    params:
    - dir_path: directory path to check
    """
    if not os.path.exists(dir_path):
        print(f"Error: The directory '{dir_path}' does not exist. Please provide a valid directory.")
        return False

    elif not os.path.isdir(dir_path):
        print(f"Error: The path '{dir_path}' is not a directory. Please provide a directory path.")
        return False

    elif not os.access(dir_path, os.W_OK):
        print(f"Error: The directory '{dir_path}' is not writable. Please provide a writable directory.")
        return False

    else:
        return True

def prompt_backup_location_input():
    """
    Prompts user for config file location. Includes validation.

    Returns:
    - backup location
    """
    while True:
        backup_directory = input("Please provide the full path to the backup directory: ")

        # TODO: Add default backup location

        if not is_valid_backup_location(backup_directory):
            continue

        try:
            with open(BACKUP_DIRECTORY_CONFIG, "w") as f:
                backup_directory = backup_directory.rstrip('/')
                config_data = {"config_path": backup_directory}
                json.dump(config_data, f)
            print(f"Backup directory saved in config.")
            break

        except Exception as e:
            print(f"Error: Failed to save the backup directory to {BACKUP_DIRECTORY_CONFIG}. Reason: {e}")
            continue

    return backup_directory

def get_backup_location():
    """
    Fetches backup directory location from config.
    Prompts for input if does not exist.

    Returns:
    - Backup file name
    """
    if not os.path.exists(BACKUP_DIRECTORY_CONFIG):
        print("No database backup location provided.")
        return prompt_backup_location_input()

    else:
        try:
            with open(BACKUP_DIRECTORY_CONFIG, "r") as f:
                config_data = json.load(f)

                # If data is empty or None, prompt the user for input
                if not config_data:
                    print(f"BACKUP_DIRECTORY_CONFIG is empty.")
                    return prompt_backup_location_input()
                else:
                    return config_data["config_path"]

        except json.JSONDecodeError:
            print(f"{BACKUP_DIRECTORY_CONFIG} is not a valid JSON file or is empty.")
            return prompt_backup_location_input()

def generate_backup_name():
    """
    Generates a backup file name in format: stock-gains-db_YYYYMMDDHHMMSS.backup
    """
    current_datetime = datetime.now().strftime(BACKUP_DATETIME_STRF)

    return f"{BACKUP_PREFIX}{current_datetime}{BACKUP_EXTENSION}"

def generate_backup_file_path():
    """
    Returns full path to backup file
    """
    return f"{get_backup_location()}/{generate_backup_name()}"

def extract_datetime_from_backup_file(file):
    """
    Given a backup file, extracts the datetime

    param:
    - file
    """
    try:
        datetime_str = file[len(BACKUP_PREFIX):-len(BACKUP_EXTENSION)]
        return datetime.strptime(datetime_str, BACKUP_DATETIME_STRF)
    except ValueError:
        print(f"Warning: Could not extract datetime from backup '{file}'")
        return None

def get_sorted_backup_tuples(backup_directory):
    """
    Returns sorted list of tuples containing backup files and datetimes

    param:
    - backup_directory
    """
    backup_files = [file for file in os.listdir(backup_directory) 
                    if file.startswith(BACKUP_PREFIX) and file.endswith(BACKUP_EXTENSION)]

    backup_files_with_datetime = [
            (file, dt) for file in backup_files
            if (dt := extract_datetime_from_backup_file(file)) is not None
        ]
    backup_files_with_datetime.sort(key=lambda x: x[1])

    return backup_files_with_datetime

def remove_oldest_backup():
    """
    Deletes oldest backup if more than defined number exist
    """
    backup_directory = get_backup_location()
    sorted_backup_tuples = get_sorted_backup_tuples(backup_directory)
    
    if len(sorted_backup_tuples) > DEFAULT_BACKUPS_NUM:
        oldest_file = sorted_backup_tuples[0][0]
        oldest_file_path = os.path.join(backup_directory, oldest_file)

        try:
            os.remove(oldest_file_path)
            print(f"Deleted oldest backup as more than {DEFAULT_BACKUPS_NUM} exist: {oldest_file_path}")
        except Exception as e:
            print(f"Error: Failed to delete oldest backup: {e}")

def get_latest_backup():
    """
    Returns filename of latest backup if exists else None
    """
    backup_directory = get_backup_location()
    sorted_backup_tuples = get_sorted_backup_tuples(backup_directory)

    if sorted_backup_tuples:
        return sorted_backup_tuples[-1][0]
    else:
        return None

def backup_database():
    """
    Backs up data currently in database into file.
    """
    backup_file_path = generate_backup_file_path()

    command = [
        "pg_dump", 
        "-h", DB_CONFIG["host"], 
        "-U", DB_CONFIG["user"], 
        "-F", "c", 
        "-b", 
        "-f", backup_file_path,
        DB_CONFIG["target_db"]
    ]
    subprocess.run(command, check=True)
    print(f"Backed up database in: {backup_file_path}")
    remove_oldest_backup()

def restore_database():
    """
    Restores database from latest backup if any exist.
    Returns True if restore succeeded, False otherwise.
    """
    latest_backup = get_latest_backup()

    if latest_backup:
        backup_file_path = f"{get_backup_location()}/{latest_backup}"
        print(f"Restoring from: {backup_file_path}")
        command = [
            "pg_restore", 
            "-h", DB_CONFIG["host"], 
            "-U", DB_CONFIG["user"], 
            "-d", DB_CONFIG["target_db"], 
            backup_file_path
        ]
        try:
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError as e:
            return False
    else:
        print(f"No existing backups to populate database.")
        return False
