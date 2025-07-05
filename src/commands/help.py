DESC_BUFFER = 10

def get_max_cmd_length(options, prefix="", dash_len=2):
    max_len = 0
    for cmd, sub in options.items():
        # Add dash and space for top-level, just indentation for nested
        length = len(prefix + cmd) + (dash_len if prefix == "" else 3)
        if length > max_len:
            max_len = length
        if hasattr(sub, "options"):
            sub_len = get_max_cmd_length(sub.options, prefix + "    ", dash_len)
            if sub_len > max_len:
                max_len = sub_len
    return max_len

def print_commands(options, commandDescriptionsObj, prefix="", pad=0, dash_len=2):
    for cmd, sub in options.items():
        desc = commandDescriptionsObj.get(cmd, "")
        if prefix == "":
            cmd_str = f"- {cmd}"
            left = cmd_str.ljust(pad)
        else:
            cmd_str = f"{prefix}{cmd}"
            left = (" " * dash_len + cmd_str).ljust(pad)
        print(f"{left}{' ' * DESC_BUFFER}{desc}")
        if hasattr(sub, "options"):
            print_commands(sub.options, commandDescriptionsObj, prefix=prefix + "    ", pad=pad, dash_len=dash_len)

def outputHelp(commandsObj, commandsDescriptionsObj):
    """
    Outputs a help message with available commands and their descriptions.

    Param:
    - commandsObj: A NestedCompleter object containing available commands.
    """
    print("Available commands:")
    pad = get_max_cmd_length(commandsObj.options)
    print_commands(commandsObj.options, commandsDescriptionsObj, pad=pad)
    print("")