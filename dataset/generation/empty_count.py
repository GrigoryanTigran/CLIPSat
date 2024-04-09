import os
import sys
import pandas as pd

def count_empty_csv(directory):
    """
    Counts the number of empty CSV files in a given directory, including its subdirectories,
    using Pandas to determine if a CSV file is empty.

    Parameters:
    - directory: The path to the directory to search in.

    Returns:
    - The number of empty CSV files found.
    """
    empty_count = 0
    parser_error_count = 0

    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check if the file is a CSV
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                # Attempt to read the CSV file
                try:
                    df = pd.read_csv(file_path, sep=';', low_memory=False)
                    # Check if the DataFrame is empty
                    if df.empty:
                        empty_count += 1
                except pd.errors.EmptyDataError:
                    # Catch the case where the CSV is completely empty (no headers)
                    empty_count += 1
                except pd.errors.ParserError:
                    # Handle parsing errors, such as mismatched number of fields
                    parser_error_count += 1

                except Exception as e:
                    # Handle other potential exceptions, such as parsing errors
                    print(f"Error reading {file_path}: {e}")
    print("Number of CSV's with parsing errors", parser_error_count)

    return empty_count

# Example usage
directory = sys.argv[1]
print(f"Number of empty CSV files: {count_empty_csv(directory)}")

