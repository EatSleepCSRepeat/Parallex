import os
import re
from datetime import datetime

# Color codes
RED = '\033[91m'
GREY = '\033[90m'
RESET = '\033[0m'

def determine_type(value):
    """Determine the type of the variable."""
    try:
        # Try to convert to integer
        int(value)
        return 'int'
    except ValueError:
        return 'str'

def read_code_log(filename):
    # Check if the file has a .cup extension
    if not filename.endswith('.prc'):
        print("Error: Only .prc files are supported.")
        return

    # Dictionary to store variables and their types
    variables = {}

    # Read the .cup file
    with open(filename, 'r') as file:
        inside_if = False
        if_block = []

        for line in file:
            line = line.strip()
            # Check for variable set command
            set_match = re.match(r'set (\w+) (.+)', line)
            if set_match:
                varname = set_match.group(1)
                varvalue = set_match.group(2).strip()
                # Store the value and type in the variables dictionary
                variables[varname] = {
                    'val': varvalue.strip('"').strip("'"),  # Remove surrounding quotes
                    'type': determine_type(varvalue)        # Determine the type
                }
            # Check for log calls and extract the message
            elif line.startswith('log '):
                # Extract the message after 'log '
                message = line[4:].strip().strip('"').strip("'")
                # Replace variables in the message
                for var in variables:
                    message = message.replace(f'&[{var}.val]', variables[var]['val'])
                    message = message.replace(f'&{{{var}.type}}', f"<{variables[var]['type']}>")
                
                # Check for undefined variables and format error message
                for var in re.findall(r'&\[(\w+)\.val\]', message):
                    if var not in variables:
                        error_message = f"ERROR: Variable '{var}' does not exist."
                        error_output = (f"{RED}ERROR{RESET} {GREY}[from {datetime.now().strftime('%H:%M:%S')}] {RESET}{error_message}")
                        print(error_output)
                        break  # Exit after printing the error
                else:
                    print(message)

            # Check for if statements
            elif line.startswith('if '):
                inside_if = True
                condition = line[3:].strip()
                varname_match = re.match(r'\(\s*(\w+)\s*\)\s*is\s*\(\s*(.+?)\s*\)', condition)
                if varname_match:
                    varname = varname_match.group(1)
                    value = varname_match.group(2).strip('"').strip("'")
                    # Store the variable check in if_block
                    if_block = [varname, value]
                else:
                    return
            elif line == ']':
                if inside_if:
                    # Evaluate the if condition
                    varname, value = if_block if len(if_block) == 2 else (None, None)
                    if varname and varname in variables:
                        if variables[varname]['val'] == value:
                            # If condition is true, process the block
                            print(f"Condition met for {varname}: executing block.")
                            for block_line in if_block:
                                # Process log statements within the if block
                                if block_line.startswith('log '):
                                    message = block_line[4:].strip().strip('"').strip("'")
                                    # Replace variables in the message
                                    for var in variables:
                                        message = message.replace(f'&[{var}.val]', variables[var]['val'])
                                        message = message.replace(f'&{{{var}.type}}', f"<{variables[var]['type']}>")
                                    print(message)
                    else:
                        error_message = f"ERROR: Variable '{varname}' does not exist."
                        error_output = (f"{RED}ERROR{RESET} {GREY}[from {datetime.now().strftime('%H:%M:%S')}] {RESET}{error_message}")
                        print(error_output)
                    inside_if = False
                    if_block = []
            elif inside_if:
                if_block.append(line)

read_code_log('src/codelog.prc')
