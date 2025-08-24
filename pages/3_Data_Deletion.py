# pages/3_Data_Deletion.py
import streamlit as st

st.set_page_config(page_title="Data Deletion")
st.title("Data Deletion Instructions")

st.info("Our application does not store your personal data on any servers.")

st.write("""
When you log in, we use a temporary access token provided by Facebook which is stored
only in your browser's current session. This token is automatically deleted when you
close your browser tab. We do not have a user database.
""")

st.write("""
To completely remove our app's permissions from your Facebook account, you can do so
by visiting your **Business Integrations** settings on Facebook.
""")

st.link_button("Go to Facebook Business Integrations", "https://www.facebook.com/settings/?tab=business_tools")

st.write("""
If you have any questions or concerns, please contact us at the email address listed in our Privacy Policy.
""")