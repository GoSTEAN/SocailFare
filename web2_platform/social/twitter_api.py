import os
import tweepy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Twitter API credentials
api_key = os.getenv('TWITTER_API_KEY')
api_secret = os.getenv('TWITTER_API_SECRET')
access_token = os.getenv('TWITTER_ACCESS_TOKEN')
access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

# Authenticate with Twitter
auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_token_secret)

# Create API object
api = tweepy.API(auth)

def post_to_twitter(content, image_path=None):
    """
    Post content to Twitter
    Args:
        content (str): The text content to post
        image_path (str, optional): Path to image file to upload
    Returns:
        tweepy.Status: The posted tweet
    """
    try:
        if image_path:
            # Upload image and post tweet with media
            media = api.media_upload(image_path)
            tweet = api.update_status(status=content, media_ids=[media.media_id])
        else:
            # Post text-only tweet
            tweet = api.update_status(status=content)
        return tweet
    except Exception as e:
        raise Exception(f"Twitter API error: {str(e)}")
