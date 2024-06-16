import schedule
import time

def post_to_social_media():
    # Add your code here to post to social media
    print("Posting to social media...")

# Schedule a post every day at 9:00 AM
schedule.every().day.at("09:00").do(post_to_social_media)

while True:
    schedule.run_pending()
    time.sleep(1)