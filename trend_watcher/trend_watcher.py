# TrendWatcher class to find trending tweets and Reddit posts
import tweepy
import praw
import logging
from dotenv import load_dotenv
import os



logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(message)s')

load_dotenv()

X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")


class TrendWatcher:
	def __init__(self, x_bearer_token=None, x_api_secret=None, x_access_token=None, x_access_token_secret=None,
				 reddit_client_id=None, reddit_client_secret=None, reddit_user_agent=None):
		# X (Twitter) API credentials
		self.x_bearer_token = x_bearer_token or X_BEARER_TOKEN

		# Reddit API credentials
		self.reddit_client_id = reddit_client_id or REDDIT_CLIENT_ID
		self.reddit_client_secret = reddit_client_secret or REDDIT_CLIENT_SECRET
		self.reddit_user_agent = reddit_user_agent or REDDIT_USER_AGENT

	def get_trendy_tweets(self, query, count=10):
		"""
		Fetch trending tweets from X (Twitter) based on a query.
		Args:
			query (str): Search query for tweets.
			count (int): Number of tweets to fetch.
		Returns:
			list: List of trending tweets (dicts with 'text' and 'user').
		"""
		# Authenticate with X (Twitter) API
		client = tweepy.Client(bearer_token=self.x_bearer_token)
		try:
			# API manual: https://docs.x.com/x-api/posts/search-recent-posts
			tweets = client.search_recent_tweets(query=query, max_results=count,
										tweet_fields=['text','created_at','author_id','public_metrics'])
			return [{
				'text': tweet.text,
				'user': tweet.username,
				'created_at': tweet.created_at
			} for tweet in tweets]
		except Exception as e:
			print(f"Error fetching tweets: {e}")
			return []

	def get_trendy_reddit_posts(self, subreddit, search_word= None, count=10):
		"""
		Fetch trending posts from Reddit based on a subreddit.
		Args:
			subreddit (str): Subreddit to search for trending posts.
			count (int): Number of posts to fetch.
		Returns:
			list: List of trending Reddit posts (dicts with 'title' and 'url').
		"""
		reddit = praw.Reddit(
			client_id=self.reddit_client_id,
			client_secret=self.reddit_client_secret,
			user_agent=self.reddit_user_agent
		)
		try:
			if search_word:
				# Search posts in the subreddit.
				posts = reddit.subreddit(subreddit).search(search_word, limit=count)
			else:
				# Get hot posts in the subreddit.
				posts = reddit.subreddit(subreddit).hot(limit=count)
			return [{
				'title': post.title,
				'url': post.url,
				'score': post.score,
				'author': str(post.author),
				'comments': post.num_comments,
			} for post in posts if not post.stickied]
		except Exception as e:
			print(f"Error fetching Reddit posts: {e}")
			return []


if __name__ == "__main__":
	# Example usage
	watcher = TrendWatcher()

	print("Trending Tweets about 'AI':")
	tweets = watcher.get_trendy_tweets("investment lang:en -is:retweet") # topic, English, no retweets.
	print(tweets)

	print("\nTrending Reddit posts from r/wallstreetbets:")
	posts = watcher.get_trendy_reddit_posts(subreddit="wallstreetbets", count=20)
	print(posts)
