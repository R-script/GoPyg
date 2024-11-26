import pytest  # Import pytest for testing
import pandas as pd 
import io  # Import io for handling byte streams
import GoPyg  # Import the script containing the application logic
from unittest.mock import patch, MagicMock  # Import tools for mocking in tests
from fastapi.testclient import TestClient  # Import TestClient for testing FastAPI applications
from GoPyg import fastapi_app  # Import the FastAPI app from GoPyg
import os 

# Initialize FastAPI test client for making requests to the app
client = TestClient(fastapi_app)

# Path to the CSV file used in tests
csv_file_path = os.path.join(os.path.dirname(__file__), 'Test Data', 'addresses.csv')

def test_upload_file():
    # Test the file upload endpoint
    with open(csv_file_path, 'rb') as f:
        response = client.post(
            "/upload",  # Endpoint for uploading files
            files={"file": ("addresses.csv", f, "text/csv")}  # File data to send
        )
    # Assert that the response is successful and contains the expected data
    assert response.status_code == 200
    assert response.json() == {"filename": "addresses.csv", "content_type": "text/csv"}

def test_load_data():
    # Test loading CSV data into a DataFrame
    with open(csv_file_path, 'rb') as f:
        file = io.BytesIO(f.read())  # Read file into a BytesIO object
        file.name = "addresses.csv"  # Set the name for the file object
        df = GoPyg.load_data(file)  # Load data using the GoPyg function

        # Verify that the result is a DataFrame
        assert isinstance(df, pd.DataFrame)

        # Verify the shape of the DataFrame matches expected dimensions
        assert df.shape == (5, 6)  # Update this based on the actual number of rows and columns

def test_preprocess_data():
    # Test the preprocessing function on a sample DataFrame
    df = pd.DataFrame({
        'col1': [1, None, 3],  # Example data with NaN values
        'col2': [None, 4, 5]
    })
    processed_df = GoPyg.preprocess_data(df)  # Process the DataFrame
    assert processed_df.isnull().sum().sum() == 0  # Ensure there are no NaN values
    assert processed_df.shape[0] <= 10000  # Check that the number of rows does not exceed the limit

def test_visualization_logic():
    # Test the visualization logic by simulating session state
    mock_session_state = MagicMock()  # Create a mock for session state
    mock_session_state.counter = 0  # Initialize counter
    mock_session_state.data = None  # Initialize data

    with patch('streamlit.session_state', mock_session_state):  # Patch session state with mock
        # Simulate file upload
        with open(csv_file_path, 'rb') as f:
            uploaded_file = io.BytesIO(f.read())  # Read file into a BytesIO object
            uploaded_file.name = 'addresses.csv'  # Set the name for the uploaded file
            uploaded_file.seek(0)  # Reset the file pointer to the beginning

            # Simulate loading data
            data = GoPyg.load_data(uploaded_file)  # Load the data
            assert data is not None  # Ensure data is loaded successfully

            # Simulate state change for visualization
            GoPyg.set_visualization_mode()  # Change to visualization mode
            assert mock_session_state.counter == 1  # Check that the counter is updated correctly

            # Simulate going back to upload mode
            GoPyg.reset_to_upload_mode()  # Reset to upload mode
            assert mock_session_state.counter == 0  # Ensure counter is reset
            assert mock_session_state.data is None  # Ensure data is cleared