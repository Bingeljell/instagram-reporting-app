# instagram_reporter.py

import requests
import pandas as pd
import io
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# PowerPoint Imports
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_THEME_COLOR

class InstagramReporter:
    """
    A class to fetch, analyze, and generate reports for an Instagram Business Account.
    """
    def __init__(self, access_token: str, page_id: str, api_version: str = "v19.0"):
        """
        Initialize the Instagram Reporter.
        """
        self.access_token = access_token
        self.page_id = page_id
        self.base_url = f"https://graph.facebook.com/{api_version}"

    def get_instagram_account_id(self) -> Optional[str]:
        """Get Instagram Business Account ID from the linked Facebook Page ID."""
        url = f"{self.base_url}/{self.page_id}"
        params = {'fields': 'instagram_business_account', 'access_token': self.access_token}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('instagram_business_account', {}).get('id')
        except requests.RequestException as e:
            print(f"Error getting Instagram account ID: {e}")
            return None

    def get_posts_data(self, days_back: int) -> List[Dict]:
        """Fetch Instagram posts from the last specified number of days."""
        ig_account_id = self.get_instagram_account_id()
        if not ig_account_id:
            return []
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        url = f"{self.base_url}/{ig_account_id}/media"
        fields_to_request = (
            'id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count,thumbnail_url,'
            'children{media_url,media_type},'
            'insights.metric(impressions,reach,saved,video_views)'
        )
        params = {
            'fields': fields_to_request,
            'since': int(start_date.timestamp()),
            'until': int(end_date.timestamp()),
            'access_token': self.access_token,
            'limit': 100
        }
        
        all_posts = []
        try:
            current_url = url
            while current_url:
                response = requests.get(current_url, params=params if current_url == url else None)
                response.raise_for_status()
                data = response.json()
                posts = data.get('data', [])
                all_posts.extend(posts)
                current_url = data.get('paging', {}).get('next')
        except requests.RequestException as e:
            print(f"❌ Error fetching posts: {e}")
            if e.response is not None:
                print(f"Response Body: {e.response.text}")
            return []

        for post in all_posts:
            if 'insights' in post and 'data' in post['insights']:
                for metric in post['insights']['data']:
                    post[metric['name']] = metric['values'][0]['value']
            post.pop('insights', None)
        return all_posts

    def analyze_posts(self, posts: List[Dict]) -> Dict:
        """Analyze posts performance and generate insights."""
        if not posts: return {}
        df = pd.DataFrame(posts)
        print(f"📋 Available data fields: {list(df.columns)}")

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.day_name()

        for col in ['like_count', 'comments_count', 'reach', 'impressions', 'saved', 'video_views', 'thumbnail_url']:
            if col not in df.columns: df[col] = 0
        df = df.fillna(0)

        df['total_engagement'] = df['like_count'] + df['comments_count'] + df['saved']
        df['reach'] = df['reach'].replace(0, 1)
        df['engagement_rate_on_reach'] = (df['total_engagement'] / df['reach']).replace([float('inf'), -float('inf')], 0).fillna(0) * 100

        df_sorted = df.sort_values('engagement_rate_on_reach', ascending=False)
        top_3_posts = df_sorted.head(3)
        bottom_3_posts = df_sorted.tail(3)

        columns_to_keep = [
            'id', 'caption', 'media_type', 'engagement_rate_on_reach', 
            'reach', 'permalink', 'media_url', 'thumbnail_url'
        ]
        
        insights = {
            'total_posts': len(df),
            'avg_engagement_rate': df['engagement_rate_on_reach'].mean(),
            'total_reach': int(df['reach'].sum()),
            'total_impressions': int(df['impressions'].sum()),
            'total_likes': int(df['like_count'].sum()),
            'total_comments': int(df['comments_count'].sum()),
            'total_saves': int(df['saved'].sum()),
            'total_video_views': int(df['video_views'].sum()),
            'best_posting_hour': df.groupby('hour')['engagement_rate_on_reach'].mean().idxmax(),
            'best_posting_day': df.groupby('day_of_week')['engagement_rate_on_reach'].mean().idxmax(),
            'content_type_performance': df.groupby('media_type')['engagement_rate_on_reach'].mean().to_dict(),
            'top_3_posts': top_3_posts[columns_to_keep].to_dict('records'),
            'bottom_3_posts': bottom_3_posts[columns_to_keep].to_dict('records')
        }
        return insights

    def create_local_csv_report(self, insights: Dict) -> str:
        """
        Creates the CSV report content in-memory and returns it as a string.
        This is the complete, non-truncated version.
        """
        # Use an in-memory text buffer instead of a file
        string_buffer = io.StringIO()
        
        # --- Part 1: Summary Data ---
        summary_data = [
            ['Metric', 'Value'],
            ['Total Posts', insights.get('total_posts', 0)],
            ['Average Engagement Rate', f"{insights.get('avg_engagement_rate', 0):.2f}%"],
            ['Total Reach', f"{insights.get('total_reach', 0):,}"],
            ['Total Impressions', f"{insights.get('total_impressions', 0):,}"],
            ['Total Likes', f"{insights.get('total_likes', 0):,}"],
            ['Total Comments', f"{insights.get('total_comments', 0):,}"],
            ['Total Saves', f"{insights.get('total_saves', 0):,}"],
            ['Total Video Views', f"{insights.get('total_video_views', 0):,}"],
            ['Best Hour to Post', f"{insights.get('best_posting_hour', 'N/A')}:00"],
            ['Best Day to Post', insights.get('best_posting_day', 'N/A')],
        ]
        # Add content type performance dynamically
        for content_type, performance in insights.get('content_type_performance', {}).items():
            summary_data.append([f'{content_type} Avg Engagement', f"{performance:.2f}%"])
        
        summary_df = pd.DataFrame(summary_data, columns=['Metric', 'Value'])
        
        # --- Part 2: Post Performance Data ---
        post_performance_data = []
        
        # Process both top and bottom posts
        for post_type, posts in [('Top Performing', insights.get('top_3_posts', [])), ('Needs Improvement', insights.get('bottom_3_posts', []))]:
            for post in posts:
                post_performance_data.append({
                    'Performance Type': post_type,
                    'Caption': post.get('caption', '')[:150] + '...' if post.get('caption') and len(post.get('caption', '')) > 150 else post.get('caption', ''),
                    'Media Type': post.get('media_type', ''),
                    'Engagement Rate (%)': f"{post.get('engagement_rate_on_reach', 0):.2f}",
                    'Reach': post.get('reach', 0),
                    'Link': post.get('permalink', '')
                })
        
        posts_df = pd.DataFrame(post_performance_data)
        
        # --- Part 3: Write everything to the in-memory buffer ---
        string_buffer.write("INSTAGRAM MONTHLY REPORT\n")
        string_buffer.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        string_buffer.write("SUMMARY METRICS\n")
        summary_df.to_csv(string_buffer, index=False)
        
        string_buffer.write("\n\nPOST PERFORMANCE DETAILS\n")
        if not posts_df.empty:
            posts_df.to_csv(string_buffer, index=False)
        else:
            string_buffer.write("No detailed post data to display.\n")
            
        # Return the entire content of the buffer as a single string
        return string_buffer.getvalue()

    def create_powerpoint_report(self, insights: Dict, title_text: str, logo_path: str):
        print("--- RUNNING THE LATEST V3 OF CREATE_POWERPOINT_REPORT ---")
        """Creates a PowerPoint presentation."""
        prs = Presentation()
        title_slide_layout = prs.slide_layouts[0]
        slide = prs.slides.add_slide(title_slide_layout)
        slide.shapes.title.text = title_text if title_text else "Instagram Performance Report"
        slide.placeholders[1].text = f"Generated on {datetime.now().strftime('%Y-%m-%d')}"
        if logo_path:
            try:
                slide.shapes.add_picture(logo_path, Inches(8.5), Inches(0.5), height=Inches(0.75))
            except FileNotFoundError:
                print(f"⚠️  Logo file not found at '{logo_path}'.")

        summary_slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(summary_slide_layout)
        slide.shapes.title.text = "Monthly Performance Summary"
        tf = slide.shapes.placeholders[1].text_frame
        tf.clear()

        summary_points = {
        "Total Posts": insights.get('total_posts'),
        "Total Reach": f"{insights.get('total_reach', 0):,}",
        "Total Impressions": f"{insights.get('total_impressions', 0):,}",
        "Average Engagement Rate": f"{insights.get('avg_engagement_rate', 0):.2f}%",
        "Total Likes": f"{insights.get('total_likes', 0):,}",
        "Total Comments": f"{insights.get('total_comments', 0):,}",
        "Total Saves": f"{insights.get('total_saves', 0):,}",
        "Best Day to Post": insights.get('best_posting_day'),
        "Best Hour to Post": f"{insights.get('best_posting_hour', 'N/A')}:00",
        }
        for key, value in summary_points.items():
            p = tf.add_paragraph(); p.text = f"{key}: {value}"; p.level = 1

        self._add_collage_slide(prs, insights.get('top_3_posts', []), "Top 3 Performing Posts")
        self._add_collage_slide(prs, insights.get('bottom_3_posts', []), "Bottom 3 Performing Posts")

        powerpoint_buffer = io.BytesIO()
        prs.save(powerpoint_buffer)
        powerpoint_buffer.seek(0)

        return powerpoint_buffer

    def _add_collage_slide(self, prs: Presentation, posts: List[Dict], title: str):
        """Helper function to add a collage slide."""
        if not posts: return
        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)
        slide.shapes.title.text = title
        positions = [(Inches(0.5), Inches(1.5)), (Inches(3.7), Inches(1.5)), (Inches(6.9), Inches(1.5))]
        for i, post in enumerate(posts):
            if i >= 3: break
            url = post.get('thumbnail_url') if post.get('media_type') == 'VIDEO' else post.get('media_url')
            if not url: continue
            left, top = positions[i]
            try:
                response = requests.get(url, stream=True); response.raise_for_status()
                pic = slide.shapes.add_picture(io.BytesIO(response.content), left, top, width=Inches(2.8))
                
                # Simple Border
                pic.line.color.rgb = RGBColor(220, 220, 220); pic.line.width = Pt(1.5)
                
                # Dynamic textbox positioning
                text_top = pic.top + pic.height + Inches(0.15)
                txBox = slide.shapes.add_textbox(left, text_top, Inches(2.8), Inches(1.5))
                tf = txBox.text_frame; tf.word_wrap = True
                tf.text = (
                    f"Type: {post.get('media_type', 'N/A')}\n"
                    f"Reach: {post.get('reach', 0):,}\n"
                    f"Eng Rate: {post.get('engagement_rate_on_reach', 0):.2f}%"
                )
                for p in tf.paragraphs: p.font.size = Pt(11)
            except Exception as e:
                print(f"❌ Error processing image/text for post {post.get('id')}. Reason: {e}")

    def generate_report(self, days_back: int, report_title: str, logo_path: str):
        """
        The main method to generate all reports in-memory.
        This version is updated to call the new in-memory report functions.

        Returns:
            A tuple containing the CSV data (as a string) and the PowerPoint data (as a BytesIO object).
        """
        print("📱 Fetching Instagram posts...")
        posts = self.get_posts_data(days_back)
        if not posts:
            # For Streamlit, it's better to raise an error that the app can catch and display.
            raise ValueError("No posts were found for the selected date range. Please try a different range.")

        print(f"✅ Found {len(posts)} posts.")
        print("📊 Analyzing post performance...")
        insights = self.analyze_posts(posts)
        if not insights:
            raise ValueError("Could not generate insights from the fetched data.")

        # --- Generate files in-memory ---
        # Call the new functions. Notice they no longer need a 'filename'.
        print("\n📝 Creating CSV data in memory...")
        csv_data = self.create_local_csv_report(insights)
        
        print("🖼️  Creating PowerPoint presentation in memory...")
        pptx_data = self.create_powerpoint_report(
            insights=insights, 
            title_text=report_title, 
            logo_path=logo_path
        )
        
        print("\n✅ All reports generated successfully in memory.")
        
        # Return the data objects for the Streamlit app to handle
        return csv_data, pptx_data