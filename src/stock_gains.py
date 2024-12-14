from prompt_toolkit import prompt

from commands.portfolio_value import portfolioValue
from db.backup_handler import backup_database, restore_database
from db.db_handler import database_setup
from utils.command_completer import COMMANDS

def main():
    conn = database_setup()
    print("\nWelcome to stock-gains: Command-line portfolio information tool\n")
    while True:
        try:
            user_input = prompt("Enter command: ", complete_while_typing=True, complete_in_thread=True, completer=COMMANDS)

            if user_input == "quit":
                break
            elif user_input == "value":
                portfolioValue(conn)
            elif user_input == "buy":
                break # TODO: Use prompt_toolkit to validate? + allow esc key to cancel
            elif user_input == "sell":
                break
            elif user_input == "dividend":
                break
            elif user_input == "settings":
                break

        except KeyboardInterrupt:
            print("Exiting...")
            break

    backup_database()

if __name__ == "__main__":
    main()
