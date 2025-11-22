# TrendWatcher class to find trending tweets and Reddit posts
import tweepy
import praw
import logging
from dotenv import load_dotenv
import os
from pytrends.request import TrendReq
import googleapiclient.discovery
from TikTokApi import TikTokApi


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(message)s')

load_dotenv()

X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")
GCP_API_KEY = os.getenv("GCP_API_KEY")


class TrendWatcher:
	def __init__(self, x_bearer_token=None, x_api_secret=None, x_access_token=None, x_access_token_secret=None,
				 reddit_client_id=None, reddit_client_secret=None, reddit_user_agent=None):
		# X (Twitter) API credentials
		self.x_bearer_token = x_bearer_token or X_BEARER_TOKEN

		# Reddit API credentials
		self.reddit_client_id = reddit_client_id or REDDIT_CLIENT_ID
		self.reddit_client_secret = reddit_client_secret or REDDIT_CLIENT_SECRET
		self.reddit_user_agent = reddit_user_agent or REDDIT_USER_AGENT
		self.gcp_api_key = GCP_API_KEY

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

	def fetch_trending_searches(self):
		"""Fetch trending searches from Google Trends.
		This doesn't work..."""
		pytrend = TrendReq()
		try:
			df = pytrend.trending_searches(pn='united_states')
			return df
		except Exception as e:
			print(f"Error fetching trending searches: {e}")
			return []
		
	def get_trendy_youtube_videos(self, region_code='US', count=50):
		"""
		Fetch trending videos from YouTube based on region.
		Args:
			region_code (str): Region code (e.g., 'US', 'GB', 'IN'). Default is 'US'.
			count (int): Number of videos to fetch. Default is 10.
		Returns:
			list: List of trending YouTube videos (dicts with 'title', 'channel', 'view_count', 'url').
		"""
		try:
			youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=self.gcp_api_key)
			
			# Fetch trending videos
			request = youtube.videos().list(
				part='snippet,statistics',
				chart='mostPopular',
				regionCode=region_code,
				maxResults=count,
				fields='items(id,snippet(title,channelTitle,publishedAt),statistics(viewCount,likeCount))'
			)
			response = request.execute()
			
			return [{
				'title': item['snippet']['title'],
				'channel': item['snippet']['channelTitle'],
				'view_count': item['statistics'].get('viewCount', 0),
				'like_count': item['statistics'].get('likeCount', 0),
				'published_at': item['snippet']['publishedAt'],
				'url': f"https://www.youtube.com/watch?v={item['id']}"
			} for item in response.get('items', [])]
		except Exception as e:
			print(f"Error fetching YouTube trending videos: {e}")
			return []
	
	def get_trendy_tiktok_videos(self, hashtag=None, count=50):
		"""THIS DOESN'T WORK YET.
		Fetch trending videos from TikTok using TikTokApi.
		Args:
			hashtag (str): Hashtag to search for (e.g., 'AI', 'stocks'). If None, fetches trending/discover videos.
			count (int): Number of videos to fetch. Default is 50.
		Returns:
			list: List of trending TikTok videos (dicts with 'description', 'author', 'view_count', 'like_count', 'comment_count', 'share_count', 'url').
		"""
		try:
			api = TikTokApi()
			videos = []
			
			if hashtag:
                # Search for videos with a specific hashtag
				videos = api.getHashtagPageVideos(hashtag, amount=count)
			else:
                # Get trending videos
				videos = api.getTrendingPageVideos(amount=count)
			
			# Extract relevant information from each video
			result = []
			for video in videos:
				try:
					video_data = {
						'description': video.get('desc', '') or video.get('title', ''),
						'author': video.get('author', {}).get('uniqueId', '') or video.get('author', {}).get('id', ''),
						'view_count': int(video.get('stats', {}).get('playCount', 0) or 0),
						'like_count': int(video.get('stats', {}).get('diggCount', 0) or 0),
						'comment_count': int(video.get('stats', {}).get('commentCount', 0) or 0),
						'share_count': int(video.get('stats', {}).get('shareCount', 0) or 0),
						'video_id': video.get('id', ''),
						'url': f"https://www.tiktok.com/@{video.get('author', {}).get('uniqueId', '')}/video/{video.get('id', '')}"
					}
					result.append(video_data)
				except (KeyError, TypeError, ValueError) as e:
					logging.warning(f"Error parsing TikTok video data: {e}")
					continue
			
			return result
		except ImportError:
			logging.error("TikTokApi not installed. Install it with: pip install TikTok-Api")
			return []
		except Exception as e:
			logging.error(f"Error fetching TikTok trending videos: {e}")
			return []


if __name__ == "__main__":
	# Example usage
	watcher = TrendWatcher()

	# Test TikTok trendy videos.
	print("Trending TikTok Videos:")
	tiktok_videos = watcher.get_trendy_tiktok_videos(count=10)

	# Test YouTube trendy videos.
	# print(watcher.get_trendy_youtube_videos())
	

	# print("Trending Tweets about 'AI':")
	# tweets = watcher.get_trendy_tweets("investment lang:en -is:retweet") # topic, English, no retweets.
	# print(tweets)

	# print("\nTrending Reddit posts from r/wallstreetbets:")
	# posts = watcher.get_trendy_reddit_posts(subreddit="wallstreetbets", count=20)
	# print(posts)
