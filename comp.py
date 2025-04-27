import pandas as pd
import os
import re

# Define allowed formats and max size
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}
MAX_FILE_SIZE_MB = 3


def is_valid_file(file_path):
    """Check file format and size."""
    file_extension = file_path.split('.')[-1].lower()
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)  # Convert bytes to MB

    if file_extension not in ALLOWED_EXTENSIONS:
        return False, "Invalid file format. Only .csv and .xlsx are allowed."

    if file_size_mb > MAX_FILE_SIZE_MB:
        return False, "File size exceeds 3MB limit."

    return True, "File is valid."


def load_file(file_path):
    """Load CSV or Excel file into a DataFrame."""
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        print("File loaded successfully.")

        # Check for missing values immediately
        missing_values = df[df[['ID', 'Name', 'Definition']].isnull().any(axis=1)]
        if not missing_values.empty:
            print("Error: Missing values found in 'ID', 'Name', or 'Definition'. Please upload a corrected file.")
            print(missing_values[['ID', 'Name', 'Definition']])
            return None, "Missing values detected. Please fix and re-upload."

        return df, "File loaded successfully."
    except Exception as e:
        return None, f"Error loading file: {str(e)}"


def is_valid_id_format(id_value):
    """Check if ID contains only numbers and hierarchical dots (e.g., 2.2.1)."""
    return bool(re.match(r'^[0-9]+(\.[0-9]+)*$', str(id_value)))


def clean_data(df):
    """Perform data cleaning tasks with detailed logging."""
    if df is None or df.empty:
        return None, "Uploaded file is empty or unreadable."

    # Identifying duplicates
    print("Removing duplicates...")
    duplicate_rows = df[df.duplicated()]
    if not duplicate_rows.empty:
        print(f"Removed {len(duplicate_rows)} duplicate rows, IDs: {list(duplicate_rows['ID'])}")
        df = df.drop_duplicates()
    else:
        print("No duplicate data found.")

    # Check for duplicate IDs with different content
    duplicate_id_groups = df[df.duplicated(subset=['ID'], keep=False)]
    if not duplicate_id_groups.empty:
        print("Warning: Identical IDs detected with different content. Possible conflicting data:")
        print(duplicate_id_groups)
        return None, "Conflicting entries detected: Same ID with different content. Please review and fix manually."

    # Validate ID format
    invalid_ids = df[~df['ID'].apply(is_valid_id_format)]
    if not invalid_ids.empty:
        print("Warning: Found invalid ID formats (must be numeric only). Please correct the following:")
        print(invalid_ids[['ID']])
        return None, "Invalid ID formats detected. Please correct and re-upload."

    # Sorting IDs
    print("Sorting IDs...")
    try:
        df.loc[:, 'ID'] = df['ID'].astype(str)
        df = df.sort_values(by='ID')  # Sort to maintain hierarchy
        print("Sorting complete. Adjusted ID sequence.")
    except Exception as e:
        return None, f"ID column contains invalid values: {str(e)}"

    print("Processing complete.")
    return df, "Data cleaned successfully."


def process_uploaded_file(file_path):
    """Main function to validate, clean, and store uploaded data with step-by-step logs."""
    # Step 1: Validate file
    is_valid, message = is_valid_file(file_path)
    print(message)
    if not is_valid:
        return message

    # Step 2: Load file
    df, load_message = load_file(file_path)
    if df is None:
        return load_message

    # Step 3: Clean data
    cleaned_df, clean_message = clean_data(df)
    if cleaned_df is None:
        return clean_message

    # Step 4: Save cleaned data
    cleaned_file_path = file_path.replace(".csv", "_cleaned.csv")
    cleaned_df.to_csv(cleaned_file_path, index=False)

    return


# Example usage
file_path = "Structure - CJF_v.0.2.csv"  # Replace with uploaded file path
process_uploaded_file(file_path)
