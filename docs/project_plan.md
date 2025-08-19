# Project Plan: Instagram Reporter SaaS

## 1. Vision & Executive Summary

**Product Vision:** To create a simple, elegant, and powerful SaaS tool that allows social media managers, freelancers, and small agencies to generate beautiful, insightful Instagram performance reports with just a few clicks.

**Core Problem:** Existing social media tools are often bloated, complex, and expensive all-in-one suites. Users who only need high-quality reporting are forced to adopt complicated workflows.

**Our Solution:** A focused application that does one thing exceptionally well: generating customizable, visually appealing reports (CSV and PowerPoint) from Instagram data. The primary goal is to provide a seamless, user-friendly experience that saves time and delivers immediate value.

## 2. Core Strategy & Competitive Advantage

*   **Methodology:** We will follow a **Lean Startup / MVP (Minimum Viable Product)** approach. The strategy is to build the simplest valuable version of the product first, get it into the hands of real users to gather feedback, and iterate based on that feedback. We will prioritize functionality over perfection in the early stages.
*   **Target Audience:**
    *   Freelance Social Media Managers
    *   Small Marketing Agencies
    *   In-house Marketers at Small to Medium Businesses
*   **Competitive Advantage (USP):**
    *   **Simplicity:** A clean, intuitive interface with no unnecessary features like post scheduling or inbox management.
    *   **Focus on Reporting:** Our core focus is on creating the best possible reporting experience.
    *   **Speed:** From login to a downloaded report in under a minute.

## 3. Development Roadmap

The project will be developed in three distinct phases, moving from a local tool to a fully-fledged, secure, and deployable web application.

---

### **Phase 1: The Interactive UI (MVP)**

### **Phase 1: The Interactive UI (MVP) - ✅ COMPLETE**

*   **Goal:** Transform the command-line script into a user-friendly, interactive web application.
*   **Status:** **Completed.** The application now runs locally with a full user interface.
*   **Key Features / Tasks:**
    *   `[x]` Create `app.py` for the Streamlit front-end.
    *   `[x]` Implement UI components (date pickers, text inputs, file uploader).
    *   `[x]` Integrate the front-end with the `InstagramReporter` class.
    *   `[x]` Use `st.spinner` for progress indication.
    *   `[x]` Generate files in-memory and serve them via `st.download_button`.
    *   `[x]` Implement robust state management with `st.session_state`.

*   **Technology Stack:**
    *   **UI Framework:** Streamlit
    *   **Backend Logic:** Our existing `instagram_reporter.py` engine.
    *   **Dependencies:** `python-pptx`, `pandas`, `requests`, `python-dotenv`

---

### **Phase 2: Secure Multi-User Authentication**

*   **Goal:** Eliminate the need for `.env` files and manual token management. Allow any team member to securely connect their own Instagram accounts.
*   **User Experience:** A new user is greeted with a "Login with Facebook" button. They go through the standard Facebook permission flow and are then presented with a dropdown list of the Instagram accounts they manage.
*   **Key Features / Tasks:**
    *   **Key Features / Tasks:**
    *   `[x]` Configure "Facebook Login" in the Meta Developer App.
    *   `[x]` Implement the full OAuth 2.0 Flow.
    *   `[x]` Use `st.session_state` to manage temporary user sessions and tokens.
    *   `[x]` Dynamically fetch and display a filtered list of the user's eligible pages.

*   **Technology Stack:**
    *   **Authentication:** Facebook Graph API (OAuth 2.0)
    *   **Python Libraries:** `requests-oauthlib` (or similar) to manage the OAuth flow.
    *   **Session Management:** Streamlit `session_state`.

---

### **Phase 3: Deployment & Go-Live**

*   **Goal:** Make the application accessible to the entire team (and future customers) via a simple URL, without requiring any local installation.
*   **User Experience:** The user navigates to `your-app-name.streamlit.app` in their browser and uses the live application.
*   **Key Features / Tasks:**
    1.  Set up a GitHub repository for the project code. - Done
    2.  Create a `requirements.txt` file listing all project dependencies.
    3.  Use Streamlit Community Cloud's built-in secrets management for server-side credentials (like the Meta App ID and Secret).
    4.  Deploy the application from the GitHub repository to Streamlit Community Cloud.
*   **Technology Stack:**
    *   **Hosting Platform:** Streamlit Community Cloud
    *   **Version Control:** Git & GitHub


### **Current Status**

*   **Goal:** Enhance the quality, detail, and flexibility of the generated reports.
*   **Status:** In Progress.

### **Sprint 1: The Foundation (Core Logic & Safety) - ✅ COMPLETE**
1.  `[x]` Implement a date range limit to ensure app stability.
2.  `[x]` Segregate report analysis by content type (Static vs. Video).
3.  `[x]` Implement user-selectable sorting for Top/Bottom posts.

### **Sprint 2: Enhancing the Outputs - ✅ COMPLETE**
1.  `[x]` Add a full, raw data export CSV of all posts.
2.  `[x]` Add a comprehensive, paginated annexure to the PowerPoint report.
3.  `[x]` Enhance reports to include more granular metrics (Likes, Comments, Saves, Views).

### **Sprint 3: The "Wow" Factor (Visualizations) - ⏳ NEXT UP**
1.  `[ ]` Add charts and graphs (e.g., "Engagement by Content Type") to the PowerPoint summary.
2.  `[ ]` Create an automated "Key Insights" slide.

## 3c. Future Enhancements & Backlog

This section documents ideas and edge cases to be addressed in future sprints, after the core MVP is complete.

*   **UI/UX Overhaul:** A full visual redesign of the Streamlit app after initial user feedback is gathered.
*   **Edge Case Handling:**
    *   Implement smarter logic for Top/Bottom post selection when the dataset is small (<=6 posts) to prevent overlap.
*   **New Features:**
    *   **Facebook Page Reports:** Expand the reporting engine to generate performance reports for Facebook Pages, not just Instagram.
    *   **Report Customization:** Allow users to toggle sections of the report on/off (e.g., "I don't need the annexure slide").
    *   **Historical Comparison:** Add logic to compare the current period's performance against the previous period.
*   **SaaS Features:**
    *   Implement user account management with a persistent database.
    *   Integrate a billing provider like Stripe.
---

## 4. SaaS Architecture & Monetization

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

## 5. Consolidated Technology Stack

*   **Language:** Python 3.x
*   **Web Framework:** Streamlit
*   **Data Analysis:** Pandas
*   **API Interaction:** Requests, Requests-OAuthlib
*   **Report Generation:** python-pptx
*   **Configuration:** python-dotenv
*   **Deployment:** Streamlit Community Cloud, GitHub
*   **Future SaaS Stack:** PostgreSQL, Redis, Celery, Stripe

## 6. Notes

*   **Facebook Graph API:** Recommend a quick Google search to get up to date on the latest changes to the Facebook Graph API - especially with regards to depricated metrics such as video_views and impressions which have been replaced by just 'views'. Also to familiarise yourself with the the most recent version of the Facebook Graph API. 
*   **Edge Cases:** Need to check edge cases such as when there are a only a limited number of a type of post / video. Eg less than 6 videos or statics, in which case there might be an overlap in the Top 3 and Bottom 3 logic. 
*   **Facebook Graph API:** Always verify the latest API version and check for deprecated metrics (e.g., `impressions`, `video_views` were replaced by `views`). The API permissions, especially `instagram_manage_insights`, are critical and must be explicitly re-authorized if changed.
*   **OAuth `redirect_uri`:** This must be an *exact* match between the Meta dashboard, the dialog URL, and the token exchange URL. Be mindful of trailing slashes and `http` vs `https` (though `localhost` is a special case).
*   **Streamlit State:** `st.session_state` is essential for persisting data (like login tokens and generated reports) across user interactions. A full browser reload will clear the state.
*   **Environment Variables (`.env`):** Changes to the `.env` file require a full server restart to be loaded.