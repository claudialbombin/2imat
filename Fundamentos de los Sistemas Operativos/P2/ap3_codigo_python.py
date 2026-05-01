import sys
import pandas as pd

delim = "::"
column_names = ['UserID', 'MovieID', 'Rating', 'Timestamp']

def read_df(file_path: str, delim: str, column_names: list) -> pd.DataFrame:
    """
    Reads a CSV file into a DataFrame.

    Args:
        file_path (str): The path to the CSV file.
        delim (str): The delimiter to use.
        column_names (list): List of column names for the DataFrame.

    Returns:
        pd.DataFrame: The resulting DataFrame.
    """
    # Engine = python to be able to use delimiter of more than one character
    return pd.read_csv(file_path, delimiter=delim, names=column_names, engine='python')

def show_head(file_path: str, file_path_destination: str, n: int = 5) -> None:
    """
    Displays the first n rows of the CSV file and saves them to a destination file.

    Args:
        file_path (str): The path to the source CSV file.
        file_path_destination (str): The path to save the resulting CSV file.
        n (int, optional): Number of rows to display. Defaults to 5.

    Returns:
        None
    """
    data = read_df(file_path, delim, column_names)
    data.head(n=n).to_csv(file_path_destination)

def describe_data(file_path: str, file_path_destination: str) -> None:
    """
    Generates descriptive statistics of the DataFrame and saves them to a destination file.

    Args:
        file_path (str): The path to the source CSV file.
        file_path_destination (str): The path to save the resulting CSV file.

    Returns:
        None
    """
    data = read_df(file_path, delim, column_names)
    data.describe().to_csv(file_path_destination)

def filter_data(file_path: str, file_path_destination: str, column: str, value: int) -> None:
    """
    Filters the DataFrame by a specific column value and saves the filtered data to a destination file.

    Args:
        file_path (str): The path to the source CSV file.
        file_path_destination (str): The path to save the resulting CSV file.
        column (str): The column name to filter by.
        value (int): The value to filter the column by.

    Returns:
        None
    """
    data = read_df(file_path, delim, column_names)
    filtered_data = data[data[column] == value]
    filtered_data.to_csv(file_path_destination)

def select_percentage(file_path: str, file_path_destination: str, percentage: float) -> None:
    """
    Selects a random sample percentage of the data and saves it to a destination file.

    Args:
        file_path (str): The path to the source CSV file.
        file_path_destination (str): The path to save the resulting CSV file.
        percentage (float): The percentage of data to sample.

    Returns:
        None
    """
    data = read_df(file_path, delim, column_names)
    sample_data = data.sample(frac=percentage / 100, random_state=42)
    sample_data.to_csv(file_path_destination, index=False, sep=",", header=False)
    print(f"File with {percentage}% of the data saved to {file_path_destination}")

def main() -> None:
    """
    Main function to parse command line arguments and execute the corresponding function.

    Returns:
        None
    """
    if len(sys.argv) < 4:
        print("Usage: python ap3_codigo_python.py <command> <source_file> <destination_file> [additional arguments]")
        sys.exit(1)

    command = sys.argv[1]
    file_path_origin = sys.argv[2]
    file_path_destination = sys.argv[3]

    print(command)
    print(file_path_origin)
    print(file_path_destination)

    if command == "show_head":
        # Default value of 5, otherwise, the fourth argument
        n = int(sys.argv[4]) if len(sys.argv) > 4 else 5
        show_head(file_path_origin, file_path_destination, n)
    elif command == "describe":
        describe_data(file_path_origin, file_path_destination)
    elif command == "filter":
        # Data filtering
        if len(sys.argv) != 6:
            print("Usage: python data_manipulation.py filter <source_file> <destination_file> <column> <value>")
            sys.exit(1)
        column = sys.argv[4]
        value = int(sys.argv[5])
        filter_data(file_path_origin, file_path_destination, column, value)
    elif command == "select_percentage":
        # Select percentage to generate a new file
        if len(sys.argv) != 5:
            print("Usage: python data_manipulation.py select_percentage <source_file> <destination_file> <percentage>")
            sys.exit(1)
        percentage = float(sys.argv[4])
        select_percentage(file_path_origin, file_path_destination, percentage)
    else:
        print("Unrecognized command")

if __name__ == "__main__":
    # Set the delimiter and column names
    main()
