
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

# Set up CORS to allow requests from Streamlit
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow any origin to make requests
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FastAPI endpoint for file upload
@fastapi_app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    return {"filename": file.filename, "content_type": file.content_type}

# Function to run FastAPI in a background thread
def run_fastapi():
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000, log_level="info")

# Start FastAPI in a background thread
threading.Thread(target=run_fastapi, daemon=True).start()

# Function to load data from the uploaded file (CSV or Excel)
def load_data(file):
    if file is not None:
        # Check if file is empty
        if file.size == 0:
            st.error("The uploaded file is empty or there is another unresolved issue. Sorry for the inconvenience.")
            return None
        if file.name.endswith('.csv'):
            file.seek(0)
            return pd.read_csv(BytesIO(file.read()))
        elif file.name.endswith('.xlsx'):
            return pd.read_excel(file)
    return None

# Function to upload file to FastAPI
def upload_to_fastapi(file):
    url = "http://127.0.0.1:8000/upload"  # FastAPI local URL
    file_bytes = BytesIO(file.read())  # Read file as bytes
    files = {'file': (file.name, file_bytes, file.type)}
    response = requests.post(url, files=files)
    return response.json()

# Function to preprocess data before passing it to pygwalker
def preprocess_data(df):
    df = df.applymap(lambda x: np.nan if x is None else x)
    df = df.fillna("N/A")
    max_rows = 10000
    return df.head(max_rows)

# Callback to set visualization mode
def set_visualization_mode():
    st.session_state.counter = 1

# Callback to reset to upload mode
def reset_to_upload_mode():
    st.session_state.counter = 0
    st.session_state.data = None  # Clear uploaded data

# Main Streamlit application function
def main():
    # Set the page configuration for a wide layout
    st.set_page_config(
        page_title="Use Pygwalker In Streamlit",
        layout="wide"
    )

    # Initialize session state variables
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'counter' not in st.session_state:
        st.session_state.counter = 0

    # If counter == 1 and data exists, stay on visualization screen
    if st.session_state.counter == 1 and st.session_state.data is not None:
        st.title("Data Visualization")
        df = preprocess_data(st.session_state.data)

        try:
            pyg_app = StreamlitRenderer(df)
            pyg_app.explorer()
            # this code did not work pyg_app.explorer(width=1000, height=1000, scrolling=True, default_tab="vis")
        except Exception as e:
            st.error(f"An error occurred while visualizing the data: {e}")

        # Button to go back to the upload screen
        st.button("Go Back to Upload", on_click=reset_to_upload_mode)
    else:
        # Upload screen logic
        st.title("Data Upload Screen")
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file", 
            type=['csv', 'xlsx']
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
                st.error("Error loading file. Please upload a valid CSV or Excel file.")

if __name__ == "__main__":
    main()
