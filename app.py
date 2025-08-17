# app.py

import streamlit as st
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Import our reporting engine
from instagram_reporter import InstagramReporter
from config import DEFAULT_API_VERSION


# ====================================================================
# --- 🕵️  THIS IS OUR DEBUGGING CODE ---
# We are asking Python: "Where did you find the 'instagram_reporter' module?"
# This will print the full file path directly onto the webpage.
import instagram_reporter
st.subheader("🕵️ Debug Information")
st.write(f"**Path to the loaded 'instagram_reporter.py' file:**")
st.code(instagram_reporter.__file__)
st.divider()
# ====================================================================


# --- Page Configuration ---
# This must be the first Streamlit command in your script
st.set_page_config(
    page_title="Instagram Report Generator",
    page_icon="📊",
    layout="centered"
)

# --- App Title ---
st.title("📊 Instagram Report Generator")
st.write(
    "Welcome! This tool helps you create a CSV and PowerPoint performance report for your Instagram account. "
    "Simply choose your settings below and click 'Generate Report'."
)
st.divider() # Adds a horizontal line

# --- 1. SETTINGS & INPUT FORM ---
# We use st.form to group inputs and have a single submission button.
with st.form(key="report_form"):
    st.header("Step 1: Configure Your Report")

    # --- Date Range Selection ---
    # Create two columns for a cleaner layout
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date", 
            value=datetime.now() - timedelta(days=30) # Default to 30 days ago
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now() # Default to today
        )

    # --- Text Inputs ---
    report_title = st.text_input(
        "Report Title", 
        value="Instagram Performance Report" # Default title
    )
    output_filename = st.text_input(
        "Output Filename (without extension)",
        value=f"Instagram_Report_{datetime.now().strftime('%Y-%m')}" # Default filename
    )
    
    # --- File Uploader for Logo ---
    logo_file = st.file_uploader(
        "Upload Your Logo (Optional)",
        type=['png', 'jpg', 'jpeg']
    )

    # --- The 'Submit' button for the form ---
    submitted = st.form_submit_button("Generate Report 🚀")


# --- 2. REPORT GENERATION LOGIC ---
# This block will only run when the 'Generate Report' button is pressed.
if submitted:
    if start_date > end_date:
        st.error("Error: The start date cannot be after the end date.")
    else:
        load_dotenv()
        access_token = os.getenv("META_ACCESS_TOKEN")
        page_id = os.getenv("META_PAGE_ID")

        if not all([access_token, page_id]):
            st.error("FATAL ERROR: META_ACCESS_TOKEN and PAGE_ID must be set in your .env file.")
        else:
            with st.spinner("Generating your report... This may take a moment..."):
                try:
                    logo_path = None
                    if logo_file is not None:
                        with open(logo_file.name, "wb") as f:
                            f.write(logo_file.getbuffer())
                        logo_path = logo_file.name
                    
                    days_back = (end_date - start_date).days

                    reporter = InstagramReporter(access_token, page_id, api_version=DEFAULT_API_VERSION)
                    
                    # --- CALL THE MODIFIED ENGINE ---
                    # It now returns two in-memory file objects
                    csv_data, pptx_data = reporter.generate_report(
                        days_back=days_back,
                        report_title=report_title,
                        logo_path=logo_path
                    )
                    
                    st.success("🎉 Your reports are ready!")

                    # --- DISPLAY DOWNLOAD BUTTONS ---
                    st.divider()
                    st.header("Step 2: Download Your Reports")

                    # Create two columns for the buttons
                    dl_col1, dl_col2 = st.columns(2)
                    with dl_col1:
                        st.download_button(
                            label="📥 Download CSV Report",
                            data=csv_data,
                            file_name=f"{output_filename}.csv",
                            mime="text/csv",
                        )
                    with dl_col2:
                        st.download_button(
                            label="📥 Download PowerPoint Report",
                            data=pptx_data,
                            file_name=f"{output_filename}.pptx",
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        )

                    if logo_path and os.path.exists(logo_path):
                        os.remove(logo_path)

                except Exception as e:
                    st.error(f"An error occurred during report generation: {e}")