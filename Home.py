# Home.py

import streamlit as st
import streamlit.components.v1 as components
import os
import tempfile
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
import secrets

# Note: Remove these imports after removing logger references
# from logger_config import logger, analytics_logger

from instagram_reporter import InstagramReporter
from config import DEFAULT_API_VERSION, FACEBOOK_GRAPH_URL, MAX_DAYS_RANGE

from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired


# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(page_title="Social Media Analyst", page_icon="📊", layout="centered")
load_dotenv()

st.markdown("""
<style>
    div[data-baseweb="select"] > div:first-child { background-color: #2a2a31; }
    div[data-baseweb="popover"] ul { background-color: #3e3e4a; }
</style>
""", unsafe_allow_html=True)

APP_ID = st.secrets.get("META_APP_ID", os.getenv("META_APP_ID"))
APP_SECRET = st.secrets.get("META_APP_SECRET", os.getenv("META_APP_SECRET"))

STATE_TTL_SECONDS = 300
_state_signer = URLSafeTimedSerializer(APP_SECRET, salt="oauth-state")

if "STREAMLIT_SERVER_RUN_ON_SAVE" in os.environ:
    BASE_REDIRECT_URI = "https://socialmedia-analyst.streamlit.app/"
else:
    BASE_REDIRECT_URI = "http://localhost:8501/"


def scrub_url_bar_once():
    # avoid re-injecting on every rerun
    if st.session_state.get("_url_scrubbed"):
        return
    components.html("""
      <script>
        (function () {
          try {
            // Clean current frame URL
            const url = new URL(window.location.href);
            url.search = '';              // drop ?code&state
            if (url.hash === '#_=_') url.hash = ''; // FB artifact
            window.history.replaceState({}, document.title, url.pathname + url.hash);

            // Best effort: also try parent (may be same-origin on Streamlit Cloud)
            if (window.parent && window.parent !== window) {
              const purl = new URL(window.parent.location.href);
              purl.search = '';
              if (purl.hash === '#_=_') purl.hash = '';
              window.parent.history.replaceState({}, document.title, purl.pathname + purl.hash);
            }
          } catch (e) { /* ignore */ }
        })();
      </script>
    """, height=0)
    st.session_state["_url_scrubbed"] = True


def make_state():
    return _state_signer.dumps({"nonce": secrets.token_urlsafe(16)})

def verify_state(state):
    try:
        _state_signer.loads(state, max_age=STATE_TTL_SECONDS)
        return True
    except (BadSignature, SignatureExpired):
        return False

def get_login_url():
    state = make_state()
    scopes = "public_profile,pages_show_list,pages_read_engagement,instagram_basic,instagram_manage_insights"
    return (
        f"https://www.facebook.com/{DEFAULT_API_VERSION}/dialog/oauth?"
        f"client_id={APP_ID}&redirect_uri={BASE_REDIRECT_URI}&state={state}&scope={scopes}"
    )



def process_auth():
    if 'access_token' in st.session_state:
        return True
    if 'code' in st.query_params and 'state' in st.query_params:
        code = st.query_params.get("code")
        state = st.query_params.get("state")
        st.query_params.clear()
        if not verify_state(state):
            st.session_state['auth_error'] = "Invalid login state."
            return False

        token_url = f"{FACEBOOK_GRAPH_URL}/{DEFAULT_API_VERSION}/oauth/access_token"
        try:
            r = requests.post(token_url, data={
                "client_id": APP_ID,
                "redirect_uri": BASE_REDIRECT_URI,
                "client_secret": APP_SECRET,
                "code": code,
            }, timeout=10)
            r.raise_for_status()
            data = r.json()
            access_token = data.get("access_token")
            if not access_token:
                st.session_state['auth_error'] = "No access token returned."
                return False
            st.session_state['access_token'] = access_token

            headers = {"Authorization": f"Bearer {access_token}"}
            u = requests.get(f"{FACEBOOK_GRAPH_URL}/me?fields=name,picture", headers=headers, timeout=10).json()
            st.session_state['user_name'] = u.get('name')
            st.session_state['user_picture'] = (u.get('picture') or {}).get('data', {}).get('url')

            pages = requests.get(
                f"{FACEBOOK_GRAPH_URL}/me/accounts?fields=name,instagram_business_account{{name,username}}",
                headers=headers, timeout=10
            ).json().get('data', [])
            st.session_state['user_pages'] = [p for p in pages if 'instagram_business_account' in p]
            scrub_url_bar_once()
            
            return True
        except requests.RequestException:
            st.session_state['auth_error'] = "Authentication error. Please try again."
            return False
    return False


# --- 3. MAIN APP UI ---
st.title("📊 Social Media Analyst: 1 Click IG Report Generator")

is_logged_in = process_auth()

# Show any authentication errors
if 'auth_error' in st.session_state:
    st.error(st.session_state.auth_error)
    del st.session_state.auth_error

if not is_logged_in:
    # --- LOGIN VIEW ---
    st.write("""
    Welcome to the Social Media Analyst! Our 1-click Instagram Report generator is a must have for social media managers and marketers looking to get a view into how their content has performed. 
    
    Please log in with your Facebook account to generate reports for the Instagram Business Accounts you manage.
    """)

    login_url = get_login_url()
    
    button_html = f"""
    <a href="{login_url}" target="_blank" style="text-decoration: none;">
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

    with st.expander("📖 Read this before you connect"):
        st.write("""
            For a successful connection, please ensure you meet the following requirements:
            
            - **Log in with the right Facebook Profile.** You must log in with the personal Facebook account that has been granted "Admin" access to the Facebook Page.
            - **Your Instagram account must be a Business or Creator account.** Personal Instagram accounts cannot be accessed via the API.
            - **Your Instagram account must be correctly linked to the Facebook Page.** You can check this in your Facebook Page's settings under "Linked Accounts."
            - **Grant all requested permissions.** When the Facebook login window appears, you must approve all the requested permissions for the app to function correctly.
            - **Select the Pages & Accounts.** The app will show you your Facebook accounts and the linked IG accounts. Please select the relevant ones so you can generate reports for them. 
        """)
    
    with st.expander("🔒 How we handle your data and security"):
        st.write("""
            - **We use the official Meta API.** You are logging in directly with Facebook.
            - **All communication is Encrypted.** Your login is protected with a signed, time-sensitive CSRF token, and all data is transferred over secure HTTPS.
            - **We never see your password.** The login happens on Facebook.com.
            - **Your access token is temporary.** It's stored securely in your browser session and is gone when you close the tab.
            - **We only request the permissions we need.** We ask for access to your pages and Instagram data solely to generate your reports.
        """)

else:
    # --- LOGGED IN VIEW ---
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.success(f"Logged in as **{st.session_state.get('user_name', 'User')}**")
    with col2:
        if st.session_state.get('user_picture'):
            st.image(st.session_state['user_picture'])
    
    st.divider()

    # Show any generation errors
    if 'generation_error' in st.session_state:
        st.error(st.session_state.generation_error)
        del st.session_state.generation_error
    
    # Rate limiting logic
    if 'report_timestamps' not in st.session_state:
        st.session_state.report_timestamps = []
    
    one_hour_ago = datetime.now() - timedelta(hours=1)
    st.session_state.report_timestamps = [
        ts for ts in st.session_state.report_timestamps if ts > one_hour_ago
    ]
    
    REPORTS_PER_HOUR_LIMIT = 5
    can_generate_report = len(st.session_state.report_timestamps) < REPORTS_PER_HOUR_LIMIT
    
    if not can_generate_report:
        st.warning(f"You have reached the limit of {REPORTS_PER_HOUR_LIMIT} reports per hour. Please try again later.")
    
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

            if 'report_ready' not in st.session_state:
                # Report generation form
                with st.form(key="report_form"):
                    st.header("Step 1: Configure Your Report")
                    st.info(f"Use the options below to customize your report. Please note the maximum date range is {MAX_DAYS_RANGE} days. You get a maximum of {REPORTS_PER_HOUR_LIMIT} generations an hour.", icon="💡")
                    
                    st.subheader("Select Date Range")
                    col1, col2 = st.columns(2)
                    with col1:
                        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
                    with col2:
                        end_date = st.date_input("End Date", value=datetime.now())
                    
                    st.subheader("Customize Report Details")
                    report_title = st.text_input("Report Title", value=f"{selected_page_display} Performance Report")
                    output_filename = st.text_input("Output Filename", value=f"{selected_page_display.split(' (@')[0]}_Report_{datetime.now().strftime('%Y-%m')}")
                    logo_file = st.file_uploader("Upload a Logo (Optional)", type=['png', 'jpg', 'jpeg'])

                    st.info("Decide how you want to sort your top / bottom posts", icon="💡")
                    sort_options = {
                        "Engagement Rate": "engagement_rate_on_reach",
                        "Reach": "reach",
                        "Likes": "like_count",
                        "Comments": "comments_count",
                        "Saves": "saved",
                        "Views (for Videos)": "views"
                    }
                    sort_by_display = st.selectbox(
                        "Rank Top/Bottom posts by:",
                        options=sort_options.keys()
                    )
                    
                    submitted = st.form_submit_button(
                        "Generate Report 🚀",
                        disabled=not can_generate_report
                    )

                # Handle form submission
                if submitted:
                    days_diff = (end_date - start_date).days
                    is_date_range_valid = True

                    if days_diff < 1:
                        st.error("Error: The start date must be before the end date.")
                        is_date_range_valid = False
                    elif days_diff > MAX_DAYS_RANGE:
                        st.error(f"Error: Please select a date range of {MAX_DAYS_RANGE} days or less. The current range is {days_diff} days.")
                        is_date_range_valid = False
                    
                    if is_date_range_valid:
                        if 'report_ready' in st.session_state:
                            del st.session_state['report_ready']
                        
                        with st.spinner("Generating... This may take a moment..."):
                            try:
                                logo_path = None
                                with tempfile.TemporaryDirectory() as temp_dir:
                                    if logo_file:
                                        safe_name = os.path.basename(logo_file.name).replace("\x00", "")
                                        if logo_file.size > 5 * 1024 * 1024:  # 5 MB
                                            st.error("Logo too large (max 5MB).")
                                            st.stop()  # <-- instead of return

                                        logo_path = os.path.join(temp_dir, safe_name)
                                        with open(logo_path, "wb") as f:
                                            f.write(logo_file.getbuffer())
                                    
                                    sort_by_value = sort_options[sort_by_display]
                                    
                                    reporter = InstagramReporter(st.session_state['access_token'], selected_page_id)
                                    summary_csv, raw_csv, pptx_data = reporter.generate_report(
                                        start_date=start_date, 
                                        end_date=end_date,
                                        report_title=report_title,
                                        logo_path=logo_path,
                                        sort_metric=sort_by_value,
                                        sort_metric_display=sort_by_display
                                    )
                                    
                                    st.session_state['summary_csv_data'] = summary_csv
                                    st.session_state['raw_csv_data'] = raw_csv
                                    st.session_state['pptx_report_data'] = pptx_data
                                    st.session_state['filename'] = output_filename
                                    st.session_state['report_ready'] = True

                                    # Analytics logging on success
                                    user_name = st.session_state.get('user_name', 'UnknownUser')
                                    page_name = selected_page_display.split(' (@')[0]
                                    # Note: You can uncomment these lines once you've re-added logger_config.py
                                    # analytics_logger.info(f"{user_name},{page_name},{days_diff}")
                                    
                                    st.session_state.report_timestamps.append(datetime.now())
                                    st.rerun()

                            except Exception as e:
                                # For MVP, simplified error handling without logger
                                # Log the error for your records
                                # logger.error("Report generation failed.", exc_info=True)
                                # Save the error to the session state to display it after the rerun
                                st.session_state['generation_error'] = f"An error occurred: {e}"
                                st.rerun() # Rerun to display the error message at the top of the page
                        
                        # Simple analytics tracking (replace with your preferred method)
                        user_name = st.session_state.get('user_name', 'UnknownUser')
                        page_name = selected_page_display.split(' (@')[0]
                        # analytics_logger.info(f"{user_name},{page_name},{days_diff}")  # Remove this line
                        
                        st.session_state.report_timestamps.append(datetime.now())
                        st.rerun()

            # Download section
            if 'report_ready' in st.session_state:
                st.divider()
                st.header("Step 2: Download Your Reports")
                
                dl_col1, dl_col2, dl_col3 = st.columns(3)
                with dl_col1:
                    st.download_button(
                        "📥 Download PowerPoint", 
                        st.session_state['pptx_report_data'], 
                        f"{st.session_state['filename']}.pptx"
                    )
                with dl_col2:
                    st.download_button(
                        "📥 Download Summary CSV", 
                        st.session_state['summary_csv_data'], 
                        f"{st.session_state['filename']}_Summary.csv"
                    )
                with dl_col3:
                    st.download_button(
                        "📥 Download Raw Data CSV", 
                        st.session_state['raw_csv_data'], 
                        f"{st.session_state['filename']}_RawData.csv"
                    )
                
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