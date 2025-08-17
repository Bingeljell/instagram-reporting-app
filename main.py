# main.py

import os
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Import our class from the new file
from instagram_reporter import InstagramReporter
# Import defaults from our config file
from config import DEFAULT_DAYS_BACK, DEFAULT_LOGO_PATH, DEFAULT_API_VERSION

def main():
    """
    Main function to parse arguments and run the Instagram report generator.
    """
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Generate a monthly Instagram performance report.")
    
    parser.add_argument('--start-date', type=str, help="Start date (YYYY-MM-DD).")
    parser.add_argument('--end-date', type=str, default=datetime.now().strftime('%Y-%m-%d'), help="End date (YYYY-MM-DD), defaults to today.")
    parser.add_argument('--days', type=int, default=DEFAULT_DAYS_BACK, help=f"Days to look back if no start date. Default: {DEFAULT_DAYS_BACK}.")
    parser.add_argument('--title', type=str, default="Instagram Performance Report", help="Custom title for the PowerPoint.")
    parser.add_argument('--logo', type=str, default=DEFAULT_LOGO_PATH, help=f"Path to a logo file. Default: '{DEFAULT_LOGO_PATH}'.")
    parser.add_argument('--output', type=str, default=f"Instagram_Report_{datetime.now().strftime('%Y-%m')}", help="Base name for output files.")

    args = parser.parse_args()

    access_token = os.getenv("META_ACCESS_TOKEN")
    page_id = os.getenv("META_PAGE_ID")
    if not all([access_token, page_id]):
        print("❌ Critical Error: META_ACCESS_TOKEN and META_PAGE_ID must be set in your .env file.")
        return

    if args.start_date:
        try:
            start = datetime.strptime(args.start_date, '%Y-%m-%d')
            end = datetime.strptime(args.end_date, '%Y-%m-%d')
            days_back = (end - start).days
            print(f"🗓️  Generating report from {args.start_date} to {args.end_date} ({days_back} days).")
        except ValueError:
            print("❌ Error: Invalid date format. Please use YYYY-MM-DD."); return
    else:
        days_back = args.days
        print(f"🗓️  Generating report for the last {days_back} days.")

    try:
        reporter = InstagramReporter(access_token, page_id, api_version=DEFAULT_API_VERSION)
        reporter.generate_report(
            days_back=days_back,
            sheet_name=args.output,
            report_title=args.title,
            logo_path=args.logo
        )
    except Exception as e:
        print(f"🔥🔥 An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()