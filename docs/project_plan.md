# Project Plan: Instagram Reporter SaaS

## 1. Vision & Strategy

**Product Vision:** To create a simple, elegant, and powerful SaaS tool that allows social media managers, freelancers, and small agencies to generate beautiful, insightful Instagram performance reports with just a few clicks.

**Core Problem:** Existing social media tools are often bloated, complex, and expensive all-in-one suites. Users who only need high-quality reporting are forced to adopt complicated and inefficient workflows.

**Our Solution:** A focused web application that does one thing exceptionally well: generating customizable, visually appealing reports. The primary goal is to provide a seamless user experience that saves time and delivers immediate, actionable value.

**Methodology:** We are following a **Lean Startup / MVP (Minimum Viable Product)** approach. The strategy is to build, deploy, and test the core product with a small group of users, gather feedback, and iterate based on real-world usage.

---

## 2. Project Status & Completed Milestones

We have successfully completed the initial development and deployment of a fully functional MVP.

### **Phase 1: Interactive UI - ✅ COMPLETE**
*   Transformed the original Python script into an interactive web application using Streamlit.
*   Implemented a full user interface with date selectors, text inputs, and a logo uploader.
*   Engineered the backend to generate reports (PowerPoint, Summary CSV, Raw Data CSV) in-memory.
*   Implemented robust state management (`st.session_state`) for a smooth user experience.

### **Phase 2: Secure Multi-User Authentication - ✅ COMPLETE**
*   Implemented the industry-standard **OAuth 2.0 "Login with Facebook" flow**.
*   Eliminated the need for end-users to manage secret `.env` files.
*   The application now securely fetches an access token for each user's session.
*   The UI dynamically fetches and displays a filtered list of the user's eligible Instagram Business Accounts.

### **Feature Sprint: Reporting Engine Polish - ✅ COMPLETE**
*   **Enhanced Logic:**
    *   Segregated report analysis by content type (Static vs. Video).
    *   Implemented user-selectable sorting for Top/Bottom posts based on various metrics (Reach, Likes, etc.).
    *   Added adaptive logic to handle edge cases for small datasets to prevent post overlap in Top/Bottom lists.
*   **Richer Outputs:**
    *   Upgraded reports to include modern API metrics (e.g., `views`).
    *   Added a paginated, multi-slide annexure with clickable links to the PowerPoint.
    *   Added a full, raw data export CSV for all posts in the period.
*   **Visualizations:**
    *   Added a "Performance Over Time" slide with Likes per Day and Reach per Day line charts.
    *   Added a "Content Strategy Analysis" slide comparing Engagement Rate by Type (bar chart) and Content Format Mix (pie chart).
*   **Stability & UX:**
    *   Implemented a date range limit and user-level rate limiting.
    *   Added robust, persistent error handling and user-facing instructions.
    *   Implemented a centralized logging system for errors (`app.log`) and usage analytics (`analytics.log`).

### **Phase 3: Deployment - ✅ COMPLETE**
*   Set up a version-controlled workflow using Git and a public GitHub repository.
*   Successfully deployed the application to **Streamlit Community Cloud**.
*   Configured the live application with production secrets and the correct OAuth Redirect URI.
*   The application is now live and accessible for internal testing.

---

## 3. Immediate Next Steps & Roadmap

With the MVP deployed, the immediate focus shifts to gathering feedback and planning the next iteration.

### **1. Alpha Testing (Current Step)**
*   **Goal:** Share the live application URL with the internal team and trusted "alpha" testers.
*   **Action:**
    *   Add team members as "Testers" in the Meta App dashboard.
    *   Provide them with the app URL and ask for structured feedback.
    *   Monitor the `app.log` for any hidden errors and `analytics.log` to observe usage patterns.

### **2. Future Sprints & Feature Backlog**

This backlog will be prioritized based on feedback from the alpha testing phase.

*   **UI/UX Overhaul:**
    *   A full visual redesign of the Streamlit app based on user feedback.
    *   Potential migration to a more customizable front-end framework if needed.

*   **Reporting Engine Enhancements:**
    *   **"Key Insights" Slide:** Implement a slide that uses logic (or a future LLM integration) to generate automated text summaries (e.g., "Video posts performed 35% better this month.").
    *   **Advanced Visualizations:** Add more charts like an Engagement by Hour of Day heatmap or a Reach vs. Engagement scatter plot.
    *   **Historical Comparison:** Add the ability to compare the selected date range to the previous period.

*   **New Core Features:**
    *   **Facebook Page Reports:** Expand the reporting engine to generate performance reports for Facebook Pages.
    *   **Report Customization:** Allow users to toggle sections of the report on/off.

*   **Transition to a Commercial Product (SaaS Features):**
    *   **App Review:** Submit the Meta App for review to get "Advanced Access" and move it to "Live" mode, allowing the general public to log in.
    *   **Persistent User Accounts:** Implement a database (`PostgreSQL`) to manage user accounts, subscriptions, and securely store encrypted long-lived tokens.
    *   **Billing Integration:** Integrate a payment provider like `Stripe`.
    *   **Background Jobs:** Move report generation to a background worker queue (`Celery` with `Redis`) to handle long-running reports without timing out the web app.
    *   **Centralized Logging:** Integrate a third-party logging service (e.g., Sentry, Logtail) for permanent, searchable logs.

---

---

## 4. Key Learnings & Technical Notes

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

## 5. SaaS Architecture & Monetization

This section outlines the plan for turning the tool into a commercial product.

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

## 6. Consolidated Technology Stack

*   **Language:** Python 3.x
*   **Web Framework:** Streamlit
*   **Data Analysis:** Pandas
*   **API Interaction:** Requests, Requests-OAuthlib
*   **Report Generation:** python-pptx
*   **Configuration:** python-dotenv
*   **Deployment:** Streamlit Community Cloud, GitHub
*   **Future SaaS Stack:** PostgreSQL, Redis, Celery, Stripe