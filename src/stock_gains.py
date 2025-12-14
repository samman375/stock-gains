from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings

from commands.buy import buyInvestment
from commands.dividend import dividend
from commands.fear_and_greed import fearAndGreedIndex
from commands.help import outputHelp
from commands.index_performance import indexPerformance
from commands.investment_performance import investmentPerformance
from commands.investment_history import investmentHistory
from commands.portfolio_value import portfolioValue
from commands.rebalance_suggestions import rebalanceSuggestions
from commands.sell import sellInvestment
from commands.settings import settingsCommand
from db.backup_handler import backup_database, restore_database
from db.db_handler import database_setup
from utils.constants.command_completer import COMMANDS, COMMAND_DESCRIPTIONS

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
    print("\nWelcome to stock-gains: Command-line portfolio information tool")
    fearAndGreedIndex()
    
    while True:
        try:
            user_input = prompt("Enter command: ", complete_while_typing=True, complete_in_thread=True, completer=COMMANDS)

            # TODO: Add keybindings to all commands if works
            if user_input == "quit":
                break
            elif user_input == "value":
                portfolioValue(conn, fullOutput=False)
            elif user_input == "value --full":
                portfolioValue(conn, fullOutput=True)
            elif user_input == "buy":
                buyInvestment(conn, kb)
            elif user_input == "sell":
                sellInvestment(conn, kb)
            elif user_input == "dividend":
                dividend(conn, kb)
            elif user_input == "investment-history":
                investmentHistory(conn, kb)
            elif user_input == "investment-performance":
                investmentPerformance(conn)
            elif user_input == "investment-performance --ticker":
                print("Ticker level investment performance is not implemented yet.")
            elif user_input == "index-performance":
                indexPerformance(conn)
            elif user_input == "rebalance-suggestions":
                rebalanceSuggestions(conn, kb)
            elif user_input == "portfolio-balance":
                print("Portfolio balance feature is not implemented yet.")
            elif user_input == "portfolio-growth":
                print("Portfolio growth feature is not implemented yet.")
            elif user_input == "ammend":
                print("Ammend feature is not implemented yet.")
            elif user_input == "fear-and-greed":
                fearAndGreedIndex()
            elif user_input == "help":
                outputHelp(COMMANDS, COMMAND_DESCRIPTIONS)
            elif user_input == "settings":
                settingsCommand(conn, kb)
            else:
                print("Invalid command. Please try again.")

        except KeyboardInterrupt:
            print("Exiting...")
            break

    backup_database()

if __name__ == "__main__":
    main()
