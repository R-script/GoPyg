import os 
import pytest  # For testing
import pandas as pd  
import io 
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from GoPyg import load_data, preprocess_data  # Import functions to be tested from GoPyg

# Path to the "Test Data" folder containing files for testing
test_data_folder = os.path.join(os.path.dirname(__file__), '../Test Data')

# List of test files to be used in the tests
test_files = ['addresses.csv', 'sample_data.xls', 'file_example.xlsx']  # Add more files as needed

# Parameterized test function to test loading data from different files
@pytest.mark.parametrize("filename", test_files)
def test_load_data(filename):
    file_path = os.path.join(test_data_folder, filename)
    
    # Check if the specified file exists
    assert os.path.exists(file_path), f"File not found: {file_path}"
    
    # Open the file in binary read mode
    with open(file_path, 'rb') as f:
        file = io.BytesIO(f.read())  # Read the file into a BytesIO object
        file.name = filename  # Set the name attribute for the file object
        df = load_data(file)  # Load the data using the load_data function

        # Verify that the result is a DataFrame and not empty
        assert isinstance(df, pd.DataFrame), "Loaded data is not a DataFrame."
        assert not df.empty, "DataFrame is empty after loading data."

        # Specific check for 'addresses.csv'
        #if filename == 'addresses.csv':
        #    assert df.shape[1] == 6, "The number of columns in addresses.csv is not as expected."

# Test function for preprocessing data
def test_preprocess_data():
    # Create a sample DataFrame with some NaN values for testing
    df = pd.DataFrame({
        'col1': [1, None, 3],
        'col2': [None, 4, 5]
    })
    
    processed_df = preprocess_data(df)  # Process the DataFrame

    # Check that there are no NaN values and row count is within limit
    assert processed_df.isnull().sum().sum() == 0, "There are NaN values in the processed DataFrame."
    assert processed_df.shape[0] <= 10000, "The number of rows exceeds the maximum limit."

# Run the tests if this script is executed directly
if __name__ == "__main__":
    pytest.main()
