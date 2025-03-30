from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings

from commands.buy import buyInvestment
from commands.dividend import dividend
from commands.portfolio_value import portfolioValue
from commands.sell import sellInvestment
from db.backup_handler import backup_database, restore_database
from db.db_handler import database_setup
from utils.command_completer import COMMANDS

# Define a key binding for the ESC key
kb = KeyBindings()

@kb.add('escape')
def _(event):
    raise KeyboardInterrupt

def main():
    conn = database_setup()
    if not conn:
        return

    # TODO: Prompt for if user wants to restore from backup
    print("\nWelcome to stock-gains: Command-line portfolio information tool\n")
    while True:
        try:
            user_input = prompt("Enter command: ", complete_while_typing=True, complete_in_thread=True, completer=COMMANDS)

            # TODO: Add keybindings to all commands if works
            if user_input == "quit":
                break
            elif user_input == "value":
                portfolioValue(conn)
            elif user_input == "buy":
                buyInvestment(conn, kb)
            elif user_input == "sell":
                sellInvestment(conn, kb)
            elif user_input == "dividend":
                dividend(conn, kb)
            elif user_input == "settings":
                break

        except KeyboardInterrupt:
            print("Exiting...")
            break

    backup_database()

if __name__ == "__main__":
    main()
