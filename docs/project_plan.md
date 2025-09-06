# Project Plan: Social Media Analyst SaaS

## 1. Vision & Strategy

**Product Vision:** To create a simple, elegant, and powerful SaaS tool that allows social media managers, freelancers, and small agencies to generate beautiful, insightful Instagram performance reports with just a few clicks.

**Core Problem:** Existing social media tools are often bloated, complex, and expensive all-in-one suites. Users who only need high-quality reporting are forced to adopt complicated and inefficient workflows.

**Our Solution:** A focused web application that does one thing exceptionally well: generating customizable, visually appealing reports. The primary goal is to provide a seamless user experience that saves time and delivers immediate, actionable value.

**Methodology:** We are following a **Lean Startup / MVP** approach. Having successfully deployed a functional MVP, we are now gathering user feedback to guide the development of V1.0, which will include persistent user accounts and tiered features.

---

## 2. Project Status: MVP Deployed

We have successfully completed the initial development and deployment of a fully functional MVP. The application is live on Streamlit Community Cloud and is ready for alpha testing.

### **Completed Milestones:**

*   **Phase 1: Interactive UI:** Transformed the original script into a full web application using Streamlit with a robust user interface and state management.
*   **Phase 2: Secure Authentication:** Implemented the industry-standard OAuth 2.0 "Login with Facebook" flow, eliminating the need for manual token management for end-users.
*   **Feature Sprint: Reporting Engine Polish:** Massively enhanced the reporting engine with content-type segregation, user-selectable sorting, advanced data metrics, visual charts, and a comprehensive, paginated PowerPoint annexure.
*   **Phase 3: Deployment:** Successfully deployed the application to a live, public URL on Streamlit Community Cloud with production-ready secrets management.
*   **Security Hardening:** Implemented CSRF protection (`itsdangerous`), moved all API calls to use POST requests and `Authorization: Bearer` headers, and added request timeouts.

---

## 3. Next Phase: V1.0 - Building the SaaS Foundation

With the MVP validated, the next phase focuses on building the core infrastructure for a commercial SaaS product. The primary goals are to implement persistent user accounts and introduce tiered features.

### **Sprint 1: User Account Management & Database Integration (Immediate Next Step)**

*   **Goal:** Move from temporary sessions to a persistent user database. This is the prerequisite for all SaaS features.
*   **Key Features / Tasks:**
    1.  **Provision Database:** Set up a managed PostgreSQL database (e.g., via Supabase or Heroku).
    2.  **Add Dependencies:** Integrate `SQLAlchemy` and `psycopg2-binary` into the project.
    3.  **Define User Model:** Create a `database.py` file to define the `User` table structure (id, facebook_id, name, email, tier, created_at, report_count).
    4.  **Upgrade Auth Logic:** Overhaul the `process_auth` function in `Home.py` to perform a "login or sign-up" check:
        *   On successful Facebook login, query the database for the user's `facebook_id`.
        *   If the user exists, load their data (e.g., `tier`) into the session.
        *   If the user does not exist, create a new user record in the database.
    5.  **Track Usage:** Increment a `report_count` in the database each time a user successfully generates a report, replacing the temporary analytics logger.

### **Sprint 2: Freemium Model & PDF Reporting**

*   **Goal:** Create a clear feature distinction between free/beta users and future paid users.
*   **Key Features / Tasks:**
    1.  **Add PDF Dependencies:** Integrate `Jinja2` and `WeasyPrint` for HTML-to-PDF generation.
    2.  **Create HTML Template:** Build a `report_template.html` that can be populated with report data.
    3.  **Build PDF Engine:** Create a `create_pdf_report` method in `instagram_reporter.py`.
    4.  **Implement Tiered UI:** Modify the download button logic in `Home.py` to:
        *   Check the user's `tier` from the session state.
        *   Show the "Download PDF" button for 'beta' or 'free' users.
        *   Show the "Download PowerPoint" button for 'pro' or paying users.

### **Sprint 3: Admin User Management Interface**

*   **Goal:** Create a simple, secure web interface for you (as the admin) to manage users and access codes.
*   **Key Features / Tasks:**
    1.  **Build Admin Page:** Create a new, hidden Streamlit page (e.g., `pages/Admin.py`).
    2.  **Secure Access:** Implement a simple check to ensure only your user ID can view this page.
    3.  **Display Users:** Write logic to query and display all users from the database in a table.
    4.  **Implement User Editing:** Add functionality to the admin page to:
        *   Manually change a user's `tier` (e.g., upgrade a beta tester to "Pro").
        *   View a user's `report_count`.
        *   Generate and manage special one-time-use sign-up codes.

---

## 4. Future Sprints & Feature Backlog

This backlog will be prioritized based on feedback from the alpha testing phase.

*   **UI/UX Overhaul:** A full visual redesign of the Streamlit app.

*   **Reporting Engine Enhancements:**
    *   **"Key Insights" Slide:** Implement a slide that uses logic or an LLM to generate automated text summaries.
    *   **Facebook Page Reports:** Expand the reporting engine to generate reports for Facebook Pages.
    **Richer Outputs:**
    *   Upgraded reports to include modern API metrics (e.g., `views`).
    *   Added a paginated, multi-slide annexure with clickable links to the PowerPoint.
    *   Added a full, raw data export CSV for all posts in the period.
    *   **Visualizations:**
    *   Added a "Performance Over Time" slide with Likes per Day and Reach per Day line charts.
    *   Added a "Content Strategy Analysis" slide comparing Engagement Rate by Type (bar chart) and Content Format Mix (pie chart).
*   **Commercialization:**
    *   **Billing Integration:** Integrate `Stripe` for subscription management.
*   **Stability & UX:**
    *   Implement user-level rate limiting.
    *   Implement robust, persistent error handling and user-facing instructions.
    *   Implement a centralized logging system for errors (`app.log`) and usage analytics (`analytics.log`).

---

## 5. Consolidated Technology Stack

*   **Language:** Python 3.x
*   **Web Framework:** Streamlit
*   **Data Analysis:** Pandas
*   **API Interaction:** Requests
*   **Report Generation:** python-pptx, Jinja2, WeasyPrint
*   **Database (V1.0):** PostgreSQL with SQLAlchemy
*   **Authentication:** `itsdangerous` for CSRF protection
*   **Deployment:** Streamlit Community Cloud
*   **Future SaaS Stack:** Redis, Celery for background jobs.



## 6. Key Learnings & Technical Notes

This section summarizes critical technical lessons learned during the MVP development.

*   **API Best Practices:**
    *   The Instagram Graph API's primary access point is through a linked Facebook Page.
    *   Always verify the latest API version and check for deprecated metrics (e.g., `impressions` was replaced by `views`). Use Google searches to confirm current metric status or updates to the API Graph. 
    *   High-value permissions like `instagram_manage_insights` are critical for data access and must be explicitly re-authorized by the user if changed or missed.

*   **OAuth & Security:**
    *   The `redirect_uri` for OAuth 2.0 must be an *exact string match* between the Meta dashboard and the application's code for both the dialog and token exchange steps.
    *   `localhost` is a special case for development, but the live URL is required for a deployed application's configuration.
    *   For a deployed app, secrets (`META_APP_ID`, etc.) must be managed via the hosting platform's secrets manager, not in the Git repository.

*   **Streamlit Development:**
    *   `st.session_state` is the correct and essential tool for managing user state (like login tokens and generated data) across interactions.
    *   A full browser reload will clear the `st.session_state`. This is expected behavior.
    *   Changes to external configuration files like `.env` or secrets require a full server restart to be loaded by the application. The developer menu's "Clear cache" is the best way to reset state locally.

---

## 7. Notes from previous versions: SaaS Architecture & Monetization

### **Security & Scalability:**

*   **Job Queues:** For a high volume of users, report generation will be offloaded to a background job queue (`Celery` with `Redis`) to keep the web app responsive.
*   **Database:** A managed `PostgreSQL` database (e.g., AWS RDS, Heroku Postgres) will be used to store user accounts, encrypted access tokens, and subscription data.
*   **Token Encryption:** All user Access Tokens will be encrypted at-rest in the database.
*   **Infrastructure:** The application will be hosted in a secure, managed cloud environment.

### **Pricing Model (Initial Proposal):**

*   **Free/Trial Tier:** 1 Instagram account, 3 reports/month, watermarked reports.
*   **Pro Tier (~$15/month):** 5 Instagram accounts, unlimited reports, custom branding (logo), no watermark.
*   **Agency Tier (~$49/month):** 20+ Instagram accounts, all Pro features, future team collaboration features.

### **Go-to-Market Plan:**

1.  **Alpha Release:** Build the MVP (Phase 1-3) and share with a small, trusted group for initial feedback.
2.  **Integrate Billing:** Add a payment provider like `Stripe`.
3.  **Public Beta:** Launch on platforms like Product Hunt and Indie Hackers. Offer an early-bird discount.
4.  **Iterate:** Use feedback from the first paying customers to guide all future development and feature prioritization.
