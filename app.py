# app.py

import streamlit as st
import os
import tempfile
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests

from instagram_reporter import InstagramReporter
from config import DEFAULT_API_VERSION, FACEBOOK_GRAPH_URL # Add FACEBOOK_GRAPH_URL

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(page_title="Instagram Report Generator", page_icon="📊", layout="centered")
load_dotenv()
APP_ID = os.getenv("META_APP_ID")
APP_SECRET = os.getenv("META_APP_SECRET")
BASE_REDIRECT_URI = "http://localhost:8501/"

# --- 2. HELPER & AUTHENTICATION LOGIC ---

def get_login_url():
    """Constructs the Facebook Login URL."""
    scopes = "pages_show_list,pages_read_engagement,instagram_basic,instagram_manage_insights"
    redirect_uri = BASE_REDIRECT_URI
    return (
        f"https://www.facebook.com/v19.0/dialog/oauth?"
        f"client_id={APP_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"state=st_app&"
        f"scope={scopes}"
    )

def handle_auth_callback():
    """Exchanges the authorization code for an access token."""
    auth_code = st.query_params.get("code")
    if not auth_code or 'access_token' in st.session_state:
        return

    api_version = DEFAULT_API_VERSION # Or get from config
    redirect_uri = BASE_REDIRECT_URI
    token_url = (
        f"{FACEBOOK_GRAPH_URL}/{api_version}/oauth/access_token?"
        f"client_id={APP_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"client_secret={APP_SECRET}&"
        f"code={auth_code}"
    )
    
    response = requests.get(token_url)
    st.query_params.clear()

    if response.status_code == 200 and 'access_token' in response.json():
        token_data = response.json()
        st.session_state['access_token'] = token_data['access_token']
        
        # --- THE FIX IS HERE ---
        # We are now asking for the linked Instagram account at the same time we get the page list.
        pages_url = (
            f"{FACEBOOK_GRAPH_URL}/me/accounts?"
            f"fields=name,id,instagram_business_account{{name,username}}&" # Ask for the IG account
            f"access_token={token_data['access_token']}"
        )
        # ------------------------

        pages_response = requests.get(pages_url)
        if pages_response.status_code == 200:
            all_pages = pages_response.json().get('data', [])
            # --- FILTERING LOGIC ---
            # Now, we only keep the pages that actually have an Instagram account linked.
            eligible_pages = [page for page in all_pages if 'instagram_business_account' in page]
            st.session_state['user_pages'] = eligible_pages
        
        st.rerun() 
    else:
        st.session_state['auth_error'] = f"Token exchange failed: {response.json().get('error', {}).get('message')}"
        st.rerun()

handle_auth_callback()

if 'auth_error' in st.session_state:
    st.error(st.session_state.auth_error)
    del st.session_state.auth_error 

if 'access_token' not in st.session_state:
    st.write("Welcome! Please log in with Facebook to continue.")
    st.link_button("Login with Facebook", get_login_url(), use_container_width=True)
else:
    # --- LOGGED-IN STATE (THIS IS THE MISSING CODE) ---
    st.success("You are successfully logged in!")
    st.divider()
    
    pages = st.session_state.get('user_pages', [])
    if not pages:
        st.warning("You do not seem to manage any Facebook Pages. Please ensure your account has the correct permissions and that you granted them during login.")
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()
    else:
        # --- UI FOR PAGE SELECTION AND REPORT GENERATION ---
        page_options = {page['name']: page['id'] for page in pages}
        selected_page_name = st.selectbox("Select a Facebook Page to report on:", options=page_options.keys())
        
        if selected_page_name:
            selected_page_id = page_options[selected_page_name]

            with st.form(key="report_form"):
                st.header("Step 1: Configure Your Report")
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
                with col2:
                    end_date = st.date_input("End Date", value=datetime.now())
                report_title = st.text_input("Report Title", value=f"{selected_page_name} Performance Report")
                output_filename = st.text_input("Output Filename", value=f"{selected_page_name}_Report_{datetime.now().strftime('%Y-%m')}")
                logo_file = st.file_uploader("Upload a Logo (Optional)", type=['png', 'jpg', 'jpeg'])
                submitted = st.form_submit_button("Generate Report 🚀")

            if submitted:
                # Clear old report data from session state
                if 'report_ready' in st.session_state:
                    del st.session_state['report_ready']
                
                with st.spinner("Generating... This may take a moment..."):
                    try:
                        logo_path = None
                        with tempfile.TemporaryDirectory() as temp_dir:
                            if logo_file:
                                logo_path = os.path.join(temp_dir, logo_file.name)
                                with open(logo_path, "wb") as f: f.write(logo_file.getbuffer())
                            
                            reporter = InstagramReporter(st.session_state['access_token'], selected_page_id)
                            csv_data, pptx_data = reporter.generate_report(
                                days_back=(end_date - start_date).days,
                                report_title=report_title,
                                logo_path=logo_path
                            )
                            st.session_state['csv_data'] = csv_data
                            st.session_state['pptx_data'] = pptx_data
                            st.session_state['filename'] = output_filename
                            st.session_state['report_ready'] = True
                    except Exception as e:
                        st.error(f"An error occurred: {e}")

            if 'report_ready' in st.session_state:
                st.divider()
                st.header("Step 2: Download Your Reports")
                dl_col1, dl_col2 = st.columns(2)
                with dl_col1:
                    st.download_button("📥 Download CSV", st.session_state['csv_data'], f"{st.session_state['filename']}.csv")
                with dl_col2:
                    st.download_button("📥 Download PowerPoint", st.session_state['pptx_data'], f"{st.session_state['filename']}.pptx")

        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()