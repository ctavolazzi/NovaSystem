import os
import tweepy
from dotenv import load_dotenv
from openai import OpenAI
import time

load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_tweet_text(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant named Nova. You are helping a user generate a tweet."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=50,
    )
    tweet_text = response.choices[0].message.content
    tweet_text += "\n\n- Nova 🤖 #AIGeneratedTweet #NovaSystem"  # Add the AI-generated tweet tag
    print("TWEET TEXT", tweet_text)
    return tweet_text

def send_tweet(tweet_text):
    consumer_key = os.environ.get("CONSUMER_KEY")
    consumer_secret = os.environ.get("CONSUMER_SECRET")
    access_token = os.environ.get("ACCESS_TOKEN")
    access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
    bearer_token = os.environ.get("BEARER_TOKEN")

    # Authenticate to Twitter
    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )

    # Send tweet
    try:
        client.create_tweet(text=tweet_text)
        print("Tweet sent successfully!")
    except tweepy.TweepyException as e:
        print("Error sending tweet: {}".format(e.reason))

def main():
    """
    The main function that orchestrates the script.
    """
    prompt = input("What should I tweet? ")
    tweet_content = generate_tweet_text(prompt)
    print(tweet_content)
    send_tweet(tweet_content)

if __name__ == "__main__":
    main()