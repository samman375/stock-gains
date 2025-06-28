from prompt_toolkit import prompt
import utils.input_validation as v

def getBoolInput(message, key_bindings):
    """
    Get a boolean input from the user.
    """
    try:
        user_input = prompt(message, validator=v.BooleanValidator(), key_bindings=key_bindings)
        if user_input.lower() in v.YES_TEXT:
            return True
        elif user_input.lower() in v.NO_TEXT:
            return False

    except KeyboardInterrupt:
        print("Operation cancelled.")
