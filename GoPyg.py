
import pandas as pd
import numpy as np
import streamlit as st
import requests
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import threading
from io import BytesIO
from pygwalker.api.streamlit import StreamlitRenderer

# FastAPI app setup
fastapi_app = FastAPI()

# Allowing fastAPI middleware to interact with streamlit
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow any origin to make requests
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FastAPI file upload
@fastapi_app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    return {"filename": file.filename, "content_type": file.content_type}

# Run fastAPI locally as backend server
def run_fastapi():
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000, log_level="info")

# Start FastAPI in background
threading.Thread(target=run_fastapi, daemon=True).start()

# Load file data 
def load_data(file):
    if file is not None:
        # Check if file is empty
        if file.size == 0:
            st.error("The uploaded file is empty or there is another unresolved issue. Sorry for the inconvenience.")
            return None
        # If file is csv reset to start point and read bytes from io
        if file.name.endswith('.csv'):
            file.seek(0)
            return pd.read_csv(BytesIO(file.read()))
        # read excel files normally
        elif file.name.endswith('.xls','.xlsx'):
            return pd.read_excel(file)
    # default return
    return None

# Function to upload file to FastAPI local
def upload_to_fastapi(file):
    url = "http://127.0.0.1:8000/upload"  # local URL
    file_bytes = BytesIO(file.read())  # Read file as bytes
    files = {'file': (file.name, file_bytes, file.type)}
    response = requests.post(url, files=files)
    # Send JSON data response
    return response.json()

# Preprocess data before passing it to pygwalker
def preprocess_data(df):
    df = df.applymap(lambda x: np.nan if x is None else x)
    # Replace empty with N/A
    df = df.fillna("N/A")
    # Limit rows to 10k
    max_rows = 10000
    return df.head(max_rows)
##########################################
#this section needs updated, non-functional

# Test function to prevent page revert
def set_visualization_mode():
    st.session_state.counter = 1

# Test function to prevent page revert
def reset_to_upload_mode():
    st.session_state.counter = 0
    st.session_state.data = None 
##########################################
# Main Streamlit app function
def main():
    # Set wide layout and streamlit title
    st.set_page_config(
        page_title="GoPyG",
        layout="wide"
    )

    # Initialize session state variables
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'counter' not in st.session_state:
        st.session_state.counter = 0 # counter is currently non-functional

    # If counter == 1 and data exists, stay on visualization screen (not functional)
    if st.session_state.counter == 1 and st.session_state.data is not None:
        st.title("Data Visualization")
        df = preprocess_data(st.session_state.data)

        try:
            # opens pygwalker display window using dataframe
            pyg_app = StreamlitRenderer(df)
            pyg_app.explorer()

        # this exception should never appear but just incase...
        except Exception as e:
            st.error(f"An error occurred while visualizing the data: {e}")

        # Button to go back to the upload screen
        st.button("Go Back to Upload", on_click=reset_to_upload_mode)
    else:
        # Upload screen logic
        st.title("Welcome: Select Upload File")
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file", 
            type=['csv', 'xlsx','xls']
        )

        if uploaded_file is not None:
            response = upload_to_fastapi(uploaded_file)
            st.write(response)  # Show FastAPI response

            # Load the uploaded file
            data = load_data(uploaded_file)

            if data is not None:
                st.session_state.data = data  # Store data
                st.success("File uploaded successfully!")
                st.write("Preview of your data:")
                st.dataframe(data)

                # Button to proceed to visualization with a callback
                st.button("Proceed to Visualization", on_click=set_visualization_mode)
            else:
                # This error should not appear given file restrictions
                st.error("Error loading file. Please upload a valid CSV or Excel file.")

if __name__ == "__main__":
    main()
