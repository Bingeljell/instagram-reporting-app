# Home.py

import os, tempfile, requests, secrets, time
from pathlib import Path
from datetime import datetime, timedelta, timezone
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from settings import load_config, current_env
 

# --- load env files BEFORE importing anything from `database` ---
ENV = os.getenv("APP_ENV") or current_env()
here = Path(__file__).resolve().parent
for name in (f".env.{ENV}", ".env.development", ".env.dev", ".env"):
    p = here / name
    if p.exists():
        load_dotenv(p, override=False)
        break
load_dotenv(here / ".env.local", override=True)  # optional overrides

from database import engine, get_db, get_user_by_facebook_id, create_user, User


u = engine.url
st.sidebar.write({
    "ENV": ENV,
    "SUPABASE_USER set": bool(os.getenv("SUPABASE_USER")),
    "SUPABASE_HOST set": bool(os.getenv("SUPABASE_HOST")),
})
from instagram_reporter import InstagramReporter
from config import DEFAULT_API_VERSION, FACEBOOK_GRAPH_URL, MAX_DAYS_RANGE

cfg = load_config()
APP_ENV = cfg["APP_ENV"]
APP_ID = cfg["FACEBOOK_APP_ID"]
APP_SECRET = cfg["FACEBOOK_APP_SECRET"]
BASE_REDIRECT_URI = cfg["FACEBOOK_REDIRECT_URI"]


# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(page_title="Social Media Analyst", page_icon="📊", layout="centered")
load_dotenv()

STATE_TTL_SECONDS = 300
if not APP_SECRET:
    st.error("Missing APP_SECRET. Check Streamlit secrets or your .env file.")
    st.stop()

st.markdown("""
<style>
    div[data-baseweb="select"] > div:first-child { background-color: #2a2a31; }
    div[data-baseweb="popover"] ul { background-color: #3e3e4a; }
</style>
""", unsafe_allow_html=True)


STATE_TTL_SECONDS = 300
if not APP_SECRET:
    st.error("Missing APP_SECRET. Check Streamlit secrets or your .env file.")
    st.stop()

_state_signer = URLSafeTimedSerializer(APP_SECRET, salt="oauth-state")

if not BASE_REDIRECT_URI.endswith("/"):
    BASE_REDIRECT_URI += "/"


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
    scopes = "public_profile,email,pages_show_list,pages_read_engagement,instagram_basic,instagram_manage_insights"
    return (
        f"https://www.facebook.com/{DEFAULT_API_VERSION}/dialog/oauth?"
        f"client_id={APP_ID}&redirect_uri={BASE_REDIRECT_URI}&state={state}&scope={scopes}"
    )



def process_auth():
    """
    Handles the entire authentication lifecycle, with added debugging + debounce to prevent loops / 368.
    Assumes: APP_ID, APP_SECRET, BASE_REDIRECT_URI, FACEBOOK_GRAPH_URL, DEFAULT_API_VERSION,
             verify_state(), get_db(), get_user_by_facebook_id(), create_user(), datetime, html, st, requests are available.
    """
    # --- helpers scoped to this function so you can paste this block as-is ---
    import time

    def _can_exchange_now() -> bool:
        now = time.time()
        last = st.session_state.get("last_exchange_ts", 0)
        if now - last < 10:  # 10s cooldown prevents rapid retries / spam blocks (368)
            st.info("Please wait a few seconds and try again.")
            return False
        st.session_state["last_exchange_ts"] = now
        return True

    def _exchange_code(app_id: str, app_secret: str, redirect_uri: str, code: str) -> dict | None:
        token_url = f"{FACEBOOK_GRAPH_URL}/{DEFAULT_API_VERSION}/oauth/access_token"
        r = requests.get(
            token_url,
            params={
                "client_id": app_id,
                "client_secret": app_secret,
                "redirect_uri": redirect_uri,  # MUST match login redirect exactly (incl. trailing slash)
                "code": code,
            },
            timeout=20,
        )
        data = {}
        try:
            if r.headers.get("content-type", "").startswith("application/json"):
                data = r.json()
        except Exception:
            data = {}

        if r.status_code != 200:
            err = (data or {}).get("error", {})
            fbtrace = (data or {}).get("fbtrace_id") or r.headers.get("x-fb-trace-id")
            st.error(
                f"OAuth exchange failed: {err.get('message','Unknown error')} "
                f"(type={err.get('type')} code={err.get('code')} sub={err.get('error_subcode')}, "
                f"fbtrace_id={fbtrace})."
            )
            st.info(f"redirect_uri used: {redirect_uri}")
            return None
        return data
    # -----------------------------------------------------------------------

    # Already authenticated?
    if 'access_token' in st.session_state and 'user_id' in st.session_state:
        return True

    # Only handle the OAuth callback case here
    if 'code' in st.query_params and 'state' in st.query_params:
        code = st.query_params.get("code")
        state = st.query_params.get("state")

        # CSRF guard
        if not verify_state(state):
            st.session_state['auth_error'] = "Invalid login state (CSRF protection)."
            # Clear query params to avoid reruns re-triggering this
            try:
                st.query_params.clear()
            except Exception:
                pass
            st.stop()
            return False

        # Debounce the exchange to avoid hammering Graph in reruns
        if not _can_exchange_now():
            st.stop()
            return False

        # Exchange code -> access_token
        data = _exchange_code(APP_ID, APP_SECRET, BASE_REDIRECT_URI, code)
        if not data or "access_token" not in data:
            # Error already shown by _exchange_code
            st.stop()
            return False

        access_token = data["access_token"]
        st.session_state['access_token'] = access_token

        # Fetch user profile (use params to pass token; more reliable with Graph)
        user_info_url = f"{FACEBOOK_GRAPH_URL}/me"
        u_info_r = requests.get(
            user_info_url,
            params={"fields": "id,name,email,picture", "access_token": access_token},
            timeout=15
        )

        if u_info_r.status_code != 200:
            try:
                ud = u_info_r.json()
            except Exception:
                ud = {}
            err = (ud or {}).get("error", {})
            st.error(
                f"Auth Error: Could not retrieve user profile. "
                f"(code={err.get('code')} sub={err.get('error_subcode')})"
            )
            st.stop()
            return False

        u_info = u_info_r.json()
        facebook_id = u_info.get('id')
        user_name = u_info.get('name')
        user_email = u_info.get('email')

        if not facebook_id:
            st.session_state['auth_error'] = "Auth Error: Could not retrieve user ID from Facebook."
            # Clear query params so we don't loop
            try:
                st.query_params.clear()
            except Exception:
                pass
            st.stop()
            return False

        # --- DB sync (your existing logic, left intact) ---
        try:
            db = next(get_db())
            db_user = get_user_by_facebook_id(db, facebook_id=facebook_id)

            if not db_user:
                db_user = create_user(db, facebook_id=facebook_id, name=user_name, email=user_email)
                if not db_user:
                    st.session_state['auth_error'] = "DB Error: Failed to create user record."
                    db.close()
                    # Clear params & stop to avoid loops
                    try:
                        st.query_params.clear()
                    except Exception:
                        pass
                    st.stop()
                    return False
            else:
                db_user.last_login_at = datetime.now(timezone.utc)
                db.commit()
                db.refresh(db_user)
                st.session_state['user_id'] = db_user.id
                st.session_state['user_name'] = db_user.name
                st.session_state['user_picture'] = (u_info.get('picture') or {}).get('data', {}).get('url')
                st.session_state['user_tier'] = (db_user.tier or "beta").lower()
                st.session_state["subscription_expires_at"] = (
                    db_user.subscription_expires_at.isoformat() if db_user.subscription_expires_at else None
                )
        finally:
            try:
                db.close()
            except Exception:
                pass
        # --------------------------------------------------

        # Fetch pages (kept as-is; uses access_token query param)
        pages_url = f"{FACEBOOK_GRAPH_URL}/me/accounts"
        pages_response = requests.get(
            pages_url,
            params={"fields": "name,id,instagram_business_account{name,username}", "access_token": access_token},
            timeout=15
        )
        if pages_response.status_code == 200:
            all_pages = pages_response.json().get('data', [])
            eligible_pages = [page for page in all_pages if 'instagram_business_account' in page]
            st.session_state['user_pages'] = eligible_pages
        else:
            st.session_state['user_pages'] = []

        # ✅ Clear callback params and rerun to a clean URL (prevents code reuse loop)
        try:
            st.query_params.clear()
            st.rerun()
        except Exception:
            # Fallback if query_params API isn't available
            components.html(f"<script>window.location.href = '{BASE_REDIRECT_URI}';</script>")
            st.stop()

        return True

    # No callback params; not authenticated yet
    return False


def increment_user_report_count(db, user_id: int):
    """Finds a user by their ID and increments their report_count."""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.report_count += 1
        db.commit()
        print(f"--- DB: Incremented report count for user: {user.name}")


# --- 3. MAIN APP UI ---
st.title("📊 Social Media Analyst: 1 Click IG Report Generator : DEV MODE")

is_logged_in = process_auth()

# Show any authentication errors
if 'auth_error' in st.session_state:
    st.error(st.session_state.auth_error)
    del st.session_state.auth_error

if not is_logged_in:
    # --- LOGIN VIEW ---
    st.write("""
    1. Login with Email permission test (for dev mode)

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
    col1, col2, col3 = st.columns([0.6,0.3, 0.1])
    with col1:
        st.success(f"Logged in as **{st.session_state.get('user_name', 'User')}**")
        
    with col2:
        if st.session_state.get('user_picture'):
            st.image(st.session_state['user_picture'])
    with col3:
        user_tier = (st.session_state.get("user_tier") or "beta").lower()
        st.write(f"**Tier:** {user_tier}")

    st.divider()

    user_tier = (st.session_state.get('user_tier') or 'beta').lower()
    ppt_allowed = user_tier in ('pro', 'agency')
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
    
    st.session_state['oauth_processed'] = True
    if not st.session_state.get('_post_oauth_rerun'):
        try:
            st.query_params.pop("code", None)  # Remove 'code' if present
            st.query_params.pop("state", None) # Remove 'state' if present              # Streamlit ≥ ~1.30
        except Exception:
            st.experimental_set_query_params()   # legacy fallback (sets empty)
        st.session_state['_post_oauth_rerun'] = True
        try:
            st.rerun()
        except Exception:
            st.experimental_rerun()
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

                                    user_tier = (st.session_state.get('user_tier') or 'beta').lower()
                                    include_ppt = user_tier in ('pro', 'agency')   # skip PPT for free/beta
                                    include_pdf = True   
                                    
                                    reporter = InstagramReporter(st.session_state['access_token'], selected_page_id)
                                    summary_csv, raw_csv, pdf_data, pptx_data = reporter.generate_report(
                                        start_date=start_date, 
                                        end_date=end_date,
                                        report_title=report_title,
                                        logo_path=logo_path,
                                        sort_metric=sort_by_value,
                                        sort_metric_display=sort_by_display,
                                        include_pdf=include_pdf,
                                        include_ppt=include_ppt,
                                    )
                                    
                                    st.session_state['summary_csv_data'] = summary_csv
                                    st.session_state['raw_csv_data'] = raw_csv
                                    st.session_state['pptx_report_data'] = pptx_data
                                    st.session_state['pdf_report_data'] = pdf_data
                                    st.session_state['filename'] = output_filename
                                    st.session_state['report_ready'] = True

                                    # After success, get a new DB session and increment the count
                                    db = next(get_db())
                                    increment_user_report_count(db, user_id=st.session_state['user_id'])
                                    db.close()

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

                user_tier = (st.session_state.get('user_tier') or 'beta').lower()
                ppt_allowed = user_tier in ('pro', 'agency')    
                
                dl_col1, dl_col2, dl_col3, dl_col4 = st.columns(4)

                #Premium tier users get PowerPoint
                with dl_col1:
                    if ppt_allowed and st.session_state.get('pptx_report_data'):
                        st.download_button(
                            "⭐️ Download PowerPoint",
                            st.session_state['pptx_report_data'],
                            f"{st.session_state['filename']}.pptx",
                            help="Editable PPT is included in paid tiers."
                        )
                    else:
                        st.button(
                            "⭐️ Download PowerPoint",
                            disabled=True,
                            help="Upgrade to Pro to unlock PowerPoint."
                        )
                with dl_col2:
                    st.download_button("📄 Download PDF",
                        st.session_state['pdf_report_data'],
                        f"{st.session_state['filename']}.pdf")

                # Scrubs get PDF & CSV - will in fact gate keep PDF also 
                with dl_col3:
                    st.download_button(
                        "📥 Download Summary CSV", 
                        st.session_state['summary_csv_data'], 
                        f"{st.session_state['filename']}_Summary.csv"
                    )
                with dl_col4:
                    st.download_button(
                        "📥 Download Raw Data CSV", 
                        st.session_state['raw_csv_data'], 
                        f"{st.session_state['filename']}_RawData.csv"
                    )
                
                if st.button("Generate Another Report"):
                    keys_to_keep = ['access_token', 'user_name', 'user_picture', 'user_pages', 'user_id', 'user_tier']
                    for key in list(st.session_state.keys()):
                        if key not in keys_to_keep:
                            del st.session_state[key]
                    st.rerun()

    st.divider()
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()