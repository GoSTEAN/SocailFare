import tweepy
from django.conf import settings

def get_twitter_api():
    auth = tweepy.OAuthHandler(
        settings.TWITTER_API_KEY, 
        settings.TWITTER_API_SECRET
    )
    auth.set_access_token(
        settings.TWITTER_ACCESS_TOKEN, 
        settings.TWITTER_ACCESS_TOKEN_SECRET
    )
    return tweepy.API(auth)

def post_to_twitter(content, image_path=None):
    try:
        api = get_twitter_api()
        if image_path:
            # Post with image
            media = api.media_upload(image_path)
            return api.update_status(status=content, media_ids=[media.media_id])
        else:
            # Post text only
            return api.update_status(status=content)
    except Exception as e:
        raise Exception(f"Twitter API error: {str(e)}")
