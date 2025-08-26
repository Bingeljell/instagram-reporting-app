# pages/4_Terms_Of_Service.py
import os
import streamlit as st

# --- Page Configuration ---
st.set_page_config(page_title="Terms of Service", layout="wide")

# --- Helper function for styling (keeps style similar to your Privacy & Deletion pages) ---
def section_header(title: str):
    st.markdown(f"<h3>{title}</h3>", unsafe_allow_html=True)

# --- Settings (optional) ---
# You can set these via Streamlit secrets or environment variables if you want to customize.
APP_NAME = st.secrets.get("APP_NAME") or os.getenv("APP_NAME") or "Social Media Analyst"
JURISDICTION = st.secrets.get("JURISDICTION") or os.getenv("JURISDICTION") or "India"
CONTACT_EMAIL = st.secrets.get("CONTACT_EMAIL") or os.getenv("CONTACT_EMAIL")  # Optional

# --- Main Content ---
st.title(f"Terms of Service for {APP_NAME}")
st.write("Last updated: August 26, 2025")

st.write("""
Welcome to **{APP_NAME}**. By accessing or using our service, you agree to be bound by these Terms of Service (the “Terms”).
If you do not agree to these Terms, please do not use the service.
""")

section_header("1) Description of the Service")
st.write("""
{APP_NAME} helps you generate **read-only social media performance reports** using official Facebook and Instagram APIs.
The service does not post content, send messages, or modify your accounts. We are **not** affiliated with or endorsed by Meta Platforms, Inc.
""")

section_header("2) Eligibility & Acceptable Use")
st.write("""
You agree to:
- Use the service **only** for lawful purposes and in compliance with applicable laws and platform policies.
- Use the service only for Pages/Instagram Business Accounts that you are **authorized** to manage.
- Not attempt to bypass rate limits, probe security, or misuse the APIs.
- Not copy, resell, or frame the service without our prior written consent.
""")

section_header("3) Accounts & Authentication")
st.write("""
We use Facebook Login (OAuth) to authenticate you. We do not create a separate user account for you.
You are responsible for maintaining the security of your device and browser session.
""")

section_header("4) Permissions & Data")
st.write("""
We request the **minimum** read permissions required to fetch insights for report generation.
Access tokens are used **only** during your active session and are not stored on a server.
For details, please review our **Privacy Policy** and **Data Deletion** pages in the app.
""")

section_header("5) Your Content & Reports")
st.write("""
You retain all rights to any content and reports generated through the service.
You are responsible for how you use or share the generated reports and for complying with Facebook/Instagram terms.
""")

section_header("6) Third-Party Services")
st.write("""
Your use of Facebook and Instagram remains subject to their respective terms and policies.
We are not responsible for the availability or changes of any third-party platform or API.
""")

section_header("7) Availability, Changes & Beta Features")
st.write("""
We may add, change, or remove features at any time, and we may suspend or discontinue the service (in whole or part).
Certain features may be offered as beta and may not operate as expected.
""")

section_header("8) Disclaimers")
st.write("""
THE SERVICE IS PROVIDED **“AS IS”** AND **“AS AVAILABLE”** WITHOUT WARRANTIES OF ANY KIND, WHETHER EXPRESS, IMPLIED, OR STATUTORY,
INCLUDING WITHOUT LIMITATION WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.
""")

section_header("9) Limitation of Liability")
st.write("""
TO THE MAXIMUM EXTENT PERMITTED BY LAW, WE SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL,
EXEMPLARY, OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS, DATA, OR GOODWILL. OUR TOTAL LIABILITY FOR ANY CLAIMS
RELATING TO THE SERVICE SHALL NOT EXCEED THE AMOUNTS (IF ANY) PAID BY YOU TO USE THE SERVICE IN THE **THREE (3) MONTHS**
BEFORE THE EVENT GIVING RISE TO LIABILITY.
""")

section_header("10) Indemnification")
st.write("""
You agree to indemnify and hold us harmless from any claims, liabilities, damages, losses, and expenses (including reasonable attorneys’ fees)
arising out of or related to your use of the service, your violation of these Terms, or your violation of any rights of a third party.
""")

section_header("11) Termination")
st.write("""
We may suspend or terminate your access to the service at any time for any reason, including if we reasonably believe you have violated these Terms.
You may stop using the service at any time. You can also revoke the app’s permissions from your **Facebook Business Integrations** settings.
""")
st.link_button("Manage Facebook Business Integrations", "https://www.facebook.com/settings/?tab=business_tools")

section_header("12) Governing Law")
st.write(f"""
These Terms are governed by the laws of **{JURISDICTION}**, without regard to its conflict of law principles.
Any disputes will be subject to the exclusive jurisdiction of the courts located in **{JURISDICTION}**.
""")

section_header("13) Changes to These Terms")
st.write("""
We may update these Terms from time to time. When we do, we will revise the “Last updated” date at the top of this page.
Your continued use of the service after any such changes constitutes your acceptance of the new Terms.
""")

section_header("14) Contact Us")
if CONTACT_EMAIL:
    st.write(f"If you have questions about these Terms, contact us at **{CONTACT_EMAIL}**.")
else:
    st.write("If you have questions about these Terms, please use the contact details provided in our Privacy Policy.")
