# ldy_utils.py
import sys
import importlib

def check_type(value):
    """Check if a value is a string, integer, or float."""
    if isinstance(value, str):
        return "string"
    elif isinstance(value, int):
        return "integer"
    elif isinstance(value, float):
        return "float"
    else:
        return "unknown"

def print_type_report(df, column, n=5):
    """Print the type of the first n entries in a specified DataFrame column."""
    type_report = df[column].head(n).apply(check_type)
    print("Type report for column:", column)
    print(type_report)

def print_full(df):
    """Print the entire DataFrame without truncation."""
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df)

def quick_exit(msg="Exiting for debugging"):
    """Exit the program immediately with a message."""
    import sys
    print(msg)
    sys.exit()


def install_and_import(package, alias=None):
    try:
        module = importlib.import_module(package)
    except ImportError:
        print(f"{package} not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        module = importlib.import_module(package)

    # If an alias is provided, add it to the globals() with that name
    if alias:
        globals()[alias] = module
    return module



# Add other useful debugging functions as needed
