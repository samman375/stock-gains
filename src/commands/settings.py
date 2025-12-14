import pandas as pd
from tabulate import tabulate
from prompt_toolkit import prompt
from prompt_toolkit.completion import NestedCompleter

from db.crud import getAllSettings, updateSetting, deleteSetting
from utils.input_validation import SettingBooleanValidator, SettingJsonValidator
from utils.constants.defaults import SUPPORTED_SETTINGS, getDefaultSetting

def getSettingsWithDefaults(conn):
    """
    Fetches all settings from database with defaults applied.
    Returns dict of attribute -> value mappings.
    Includes defaults for any missing settings.
    """
    settings = getAllSettings(conn)

    for setting_name, config in SUPPORTED_SETTINGS.items():
        if setting_name not in settings:
            settings[setting_name] = getDefaultSetting(setting_name)
    
    return settings

def displaySettingsTable(settings):
    """
    Displays current settings in a formatted table.
    
    Params:
    - settings: dict of setting name -> value mappings
    """
    settings_rows = []
    for attr, value in sorted(settings.items()):
        if attr in SUPPORTED_SETTINGS:
            description = SUPPORTED_SETTINGS[attr]['description']
            settings_rows.append([attr, value, description])
    
    df = pd.DataFrame(settings_rows, columns=['Setting', 'Value', 'Description'])
    table = tabulate(df, headers='keys', tablefmt='rounded_grid', showindex=False, maxcolwidths=[20, 50, 30])
    
    print("\nCurrent Settings:")
    print(table)

def getSettingNameFromUser():
    """
    Prompts user to select a setting name.
    
    Returns:
    - str: valid setting name, or None if user exits
    """
    setting_names = list(SUPPORTED_SETTINGS.keys())
    settings_completer = NestedCompleter.from_nested_dict({name: None for name in setting_names + ['exit']})
    
    print("\nAvailable settings: " + ", ".join(setting_names) + "\n")
    while True:
        try:
            input_value = prompt("Enter setting name to change (or 'exit'/'ESC' to quit): ", 
                                completer=settings_completer).strip().lower()
        except KeyboardInterrupt:
            return None
        
        if input_value == 'exit' or input_value == '':
            print()
            return None
        
        if input_value in SUPPORTED_SETTINGS:
            return input_value
        
        print(f"Error: Unknown setting '{input_value}'")

def getSettingValueFromUser(setting_type, current_value):
    """
    Prompts user for a new setting value with appropriate validator.
    Pass empty input to reset to default value.
    
    Params:
    - setting_type: type of the setting (boolean, json, or other)
    - current_value: current value to display
    
    Returns:
    - str: new value, or None if cancelled, or '__DEFAULT__' to reset to default
    """
    try:
        if setting_type == 'boolean':
            bool_completer = NestedCompleter.from_nested_dict({'true': None, 'false': None})
            new_value = prompt(
                f"Enter value (true/false) [current: {current_value}] (leave empty for default): ",
                validator=SettingBooleanValidator(),
                completer=bool_completer
            ).strip().lower()
        elif setting_type == 'json':
            new_value = prompt(
                f"Enter value as list [current: {current_value}] (leave empty for default): ",
                validator=SettingJsonValidator()
            ).strip()
        else:
            new_value = prompt(f"Enter value [current: {current_value}] (leave empty for default): ").strip()
        
        if not new_value:
            return '__DEFAULT__'
        
        return new_value
    except KeyboardInterrupt:
        print("Cancelled.")
        return None

def updateAndReportSetting(conn, setting_name, new_value, current_value, is_delete=False):
    """
    Updates a setting in the database or deletes it to reset to default, and reports the result.
    
    Params:
    - conn: database connection
    - setting_name: name of the setting
    - new_value: new value for the setting (ignored if is_delete=True)
    - current_value: previous value for display
    - is_delete: if True, delete the setting instead of updating it
    """
    if is_delete:
        success, message = deleteSetting(conn, setting_name)
        if success:
            default_value = getDefaultSetting(setting_name)
            print(f"\n✓ {message}")
            print(f"\n  {setting_name}: {current_value} → {default_value} (default)")
        else:
            print(f"\n✗ {message}")
    else:
        success, message = updateSetting(conn, setting_name, new_value)
        
        if success:
            print(f"\n✓ {message}")
            print(f"\n  {setting_name}: {current_value} → {new_value}")
        else:
            print(f"\n✗ {message}")

def settingsCommand(conn, kb):
    """
    Interactive settings command.
    Displays current settings and allows user to modify them.
    """
    while True:
        settings = getSettingsWithDefaults(conn)
        displaySettingsTable(settings)
        
        setting_name = getSettingNameFromUser()
        if setting_name is None:
            break
        
        current_value = settings.get(setting_name, SUPPORTED_SETTINGS[setting_name]['default'])
        setting_type = SUPPORTED_SETTINGS[setting_name]['type']
        
        new_value = getSettingValueFromUser(setting_type, current_value)
        if new_value is None:
            continue
        
        if new_value == '__DEFAULT__':
            updateAndReportSetting(conn, setting_name, None, current_value, is_delete=True)
        else:
            updateAndReportSetting(conn, setting_name, new_value, current_value)
