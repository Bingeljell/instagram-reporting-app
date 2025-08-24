# pages/2_Privacy_Policy.py

import streamlit as st

# --- Page Configuration ---
st.set_page_config(page_title="Privacy Policy", layout="wide")

# --- Helper function for styling ---
def section_header(title):
    st.markdown(f"<h3>{title}</h3>", unsafe_allow_html=True)

# --- Main Content ---
st.title("Privacy Policy for Social Media Analyst")
st.write("Last updated: August 23, 2025")

st.markdown("""
This Privacy Policy describes our policies and procedures on the collection, use, and disclosure of your information when you use our Service.

By using the Service, you agree to the collection and use of information in accordance with this Privacy Policy.
""")

st.divider()

section_header("Interpretation and Definitions")

st.subheader("Interpretation")
st.markdown("Words with capitalized initial letters have defined meanings. These definitions apply whether they appear in singular or plural form.")

st.subheader("Definitions")
st.markdown("""
- **Application** refers to Social Media Analyst, the software program provided by us.
- **Company** (referred to as "We", "Us", or "Our") refers to 21N78E Creative Labs, A 101, Aurus Chambers. SS Amrutwar Marg. Worli. Mumbai 400013.
- **Country** refers to India.
- **Service** refers to the Application.
- **Third-party Social Media Service** refers to Facebook, through which a User logs in to use the Service.
- **You** means the individual accessing or using the Service.
""")

st.divider()

section_header("Collecting and Using Your Personal Data")

st.subheader("Types of Data Collected")
st.markdown("""
When you grant our Application access to your Facebook account, we may collect Personal Data that is already associated with your Third-Party Social Media Service's account. The specific data we collect is limited to the permissions you grant during the authentication process.
""")

st.markdown("""
**Data collected via Facebook Login:**
*   **Public Profile Information:** Your name and profile picture, as provided by Facebook. This is used to personalize your user experience within the app.
*   **List of Facebook Pages:** We receive a list of the Facebook Pages for which you have administrative rights. This is necessary to allow you to select which page you want to generate a report for.
*   **Instagram Business Account Data:** For the page you select, we access the linked Instagram Business Account to retrieve performance data about its media objects (posts, videos, etc.). This includes metrics like reach, views, likes, comments, and saves.
*   **An Access Token:** Facebook provides our application with a temporary access token that allows us to make these API calls on your behalf. This token is stored securely in your browser session and is discarded when you close the tab. **We never see or store your Facebook password.**
""")

st.subheader("Use of Your Personal Data")
st.markdown("""
We uses the collected data for the following purposes:
*   **To provide and maintain our Service:** The core purpose of collecting your data is to generate the Instagram performance reports you request.
*   **To personalize your experience:** We display your name and profile picture to confirm that you are logged in.
*   **For internal analytics:** We may log non-personally identifiable events, such as the fact that a report was generated for a page, to monitor application usage and improve our Service.
""")

st.subheader("Retention and Deletion of Your Personal Data")
st.markdown("""
We do not operate a persistent user database. Your Personal Data, including your access token, is stored only within your browser's session state (`st.session_state`). When you close your browser tab, this information is automatically deleted.

You can revoke our application's access to your data at any time from your Facebook account's "Business Integrations" settings.
""")

st.divider()

section_header("Disclosure of Your Personal Data")
st.markdown("We do not sell, trade, or transfer your personally identifiable information to outside parties. Your data is used solely for the purpose of generating reports for you within the application.")

st.divider()

section_header("Security of Your Personal Data")
st.markdown("""
The security of your data is important to us. We use the official, secure OAuth 2.0 protocol provided by Meta for authentication. All communication with the Facebook Graph API is encrypted via HTTPS. However, remember that no method of transmission over the Internet or method of electronic storage is 100% secure.
""")

st.divider()

section_header("Links to Other Websites")
st.markdown("""
Our Service may contain links to other websites that are not operated by us (for example, the links to your Instagram posts in the generated reports). If you click on a third-party link, you will be directed to that third party's site. We have no control over and assume no responsibility for the content, privacy policies, or practices of any third-party sites or services.
""")

st.divider()

section_header("Changes to this Privacy Policy")
st.markdown("""
We may update our Privacy Policy from time to time. Changes are effective when they are posted on this page.
""")

st.divider()

section_header("Contact Us")
st.markdown("""
If you have any questions about this Privacy Policy, you can contact us:
*   By email: nikhil.shahane@21n78e.com
""")