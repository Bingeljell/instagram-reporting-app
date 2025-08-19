# app.py

import streamlit as st
import os
import tempfile
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests

from instagram_reporter import InstagramReporter
from config import DEFAULT_API_VERSION, FACEBOOK_GRAPH_URL

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(page_title="Instagram Report Generator", page_icon="📊", layout="centered")
load_dotenv()
APP_ID = os.getenv("META_APP_ID")
APP_SECRET = os.getenv("META_APP_SECRET")
BASE_REDIRECT_URI = "http://localhost:8501/"

# --- 2. AUTHENTICATION LOGIC ---

def get_login_url():
    scopes = "public_profile,pages_show_list,pages_read_engagement,instagram_basic,instagram_manage_insights"
    redirect_uri = BASE_REDIRECT_URI
    api_version = DEFAULT_API_VERSION
    return (
        f"https://www.facebook.com/{api_version}/dialog/oauth?"
        f"client_id={APP_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"state=st_app&"
        f"scope={scopes}"
    )

def handle_auth_callback():
    auth_code = st.query_params.get("code")
    if not auth_code or 'access_token' in st.session_state:
        return

    redirect_uri = BASE_REDIRECT_URI
    api_version = DEFAULT_API_VERSION
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
        access_token = token_data['access_token']
        st.session_state['access_token'] = access_token
        
        user_info_url = f"{FACEBOOK_GRAPH_URL}/me?fields=name,picture&access_token={access_token}"
        user_info_response = requests.get(user_info_url)
        if user_info_response.status_code == 200:
            user_info = user_info_response.json()
            st.session_state['user_name'] = user_info.get('name')
            st.session_state['user_picture'] = user_info.get('picture', {}).get('data', {}).get('url')
        
        pages_url = f"{FACEBOOK_GRAPH_URL}/me/accounts?fields=name,id,instagram_business_account{{name,username}}&access_token={access_token}"
        pages_response = requests.get(pages_url)
        if pages_response.status_code == 200:
            all_pages = pages_response.json().get('data', [])
            eligible_pages = [page for page in all_pages if 'instagram_business_account' in page]
            st.session_state['user_pages'] = eligible_pages
        
        st.rerun() 
    else:
        st.session_state['auth_error'] = f"Token exchange failed: {response.json().get('error', {}).get('message')}"
        st.rerun()

# --- 3. MAIN APP UI ---
st.title("📊 Instagram Report Generator")

handle_auth_callback()

if 'auth_error' in st.session_state:
    st.error(st.session_state.auth_error)
    del st.session_state.auth_error 

if 'access_token' not in st.session_state:
    st.write("Welcome! Please log in with your Facebook account to generate reports for the Instagram Business Accounts you manage.")
    login_url = get_login_url()

    button_html = f"""
    <a href="{login_url}" target="_self" style="text-decoration: none;">
        <div style="
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #1877F2;
            color: white;
            padding: 0.5em 1em;
            border-radius: 0.5rem;
            border: none;
            font-size: 1rem;
            font-weight: bold;
            width: 100%;
            cursor: pointer;
            height: 2.5rem;
        ">
            Login with Facebook
        </div>
    </a>
    """
    st.markdown(button_html, unsafe_allow_html=True)
    
    
    st.divider()
    
    with st.expander("🔒 How we handle your data and security"):
        st.write("""
            - **We use the official Meta API.** You are logging in directly with Facebook.
            - **We never see your password.** The login happens on Facebook.com.
            - **Your access token is temporary.** It's stored securely in your browser session and is gone when you close the tab.
            - **We only request the permissions we need.** We ask for access to your pages and Instagram data solely to generate your reports.
        """)
else:
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.success(f"Logged in as **{st.session_state.get('user_name', 'User')}**")
    with col2:
        if st.session_state.get('user_picture'):
            st.image(st.session_state['user_picture'])
    
    st.divider()
    
    pages = st.session_state.get('user_pages', [])
    if not pages:
        st.warning("You do not seem to manage any eligible Instagram Business Accounts. Please ensure your account has the correct permissions and that you granted them during login.")
    else:
        page_options = {
            f"{page['name']} (@{page.get('instagram_business_account', {}).get('username', 'N/A')})": page['id'] 
            for page in pages
        }
        selected_page_display = st.selectbox(
            "Select the Instagram Account to report on:", 
            options=page_options.keys()
        )
        
        if selected_page_display:
            selected_page_id = page_options[selected_page_display]

            with st.form(key="report_form"):
                st.header("Step 1: Configure Your Report")
                form_col1, form_col2 = st.columns(2)
                with form_col1:
                    start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
                with form_col2:
                    end_date = st.date_input("End Date", value=datetime.now())
                report_title = st.text_input("Report Title", value=f"{selected_page_display} Performance Report")
                output_filename = st.text_input("Output Filename", value=f"{selected_page_display.split(' (@')[0]}_Report_{datetime.now().strftime('%Y-%m')}")
                logo_file = st.file_uploader("Upload a Logo (Optional)", type=['png', 'jpg', 'jpeg'])
                submitted = st.form_submit_button("Generate Report 🚀")

            if submitted:
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
        
        if st.button("Generate Another Report"):
            keys_to_keep = ['access_token', 'user_name', 'user_picture', 'user_pages']
            for key in list(st.session_state.keys()):
                if key not in keys_to_keep:
                    del st.session_state[key]
            st.rerun()

    st.divider()
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()