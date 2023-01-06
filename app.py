# import constant.py, * is the wildcard operator. In this context, in means "all".
from constants import *
from utils import * 
# import replit database
from replit import db
# flask
from flask import (
  Flask,
  render_template,
  url_for,
  request
)
app = Flask(__name__) # our app instance

# initializing context variable with default values
context = { 
  'tweets': [], 
  'news': [],
  'articles_summary': '',
  'articles_count': 0,
  'tweet_count': 0,
  'query': '',
}  


# serve landing page
@app.route('/')
def home():
  return render_template('home.html')

# takes user request & display content
@app.route('/query/', methods=['GET', 'POST'])

def query():
  """
  Serve top tweets and AI summerization. This is the home page.
  Returns nothing.
  """
  # Grabs the user input
  query = request.form['query']  
  # Save user query to context variable (optional if you don't want to display it)
  context['query'] = query 
  
  print('Running query:' + query)

  # 1. Make the API call, clean responses, and populate database
  context['articles_count'] = newsPopulateDB(query)
  
  # 2. Retrive a list of news we want to serve 
  context['news'] = getNewsFeed()
  
  # 3. Get news summary 
  context['articles_summary'] = summaryModel()

  # 4. Similar steps for twitter data, except we don't so the summaries 
  context['tweet_count'] = tweetsPopulateDB(query)
  context['tweets'] = getTweetsFeed()

  return render_template('index.html', **context)


def getTweetsFeed(query: str = query):
  """
  Retrieve top 10 most popular tweets from database and extract the 
  fields we'd like to display
  """

  new_top_tweets = []
  # Collect fields we want to display 
  # to add a field, simply add a key value pair to the tweet dictionary
  for raw in db['top10']:
    tweet = {
      'text': raw['text'],
      'id': raw['tweetID'],
      'time_posted': parseDate(raw['date']),
      'author': raw['authorID'],
      'retweets': raw['retweets'],
      'likes': raw['likes'],
      'replies': raw['replies'],
    }
    new_top_tweets.append(tweet)
  
  return new_top_tweets

def getNewsFeed():
  """
  Retrieve 10 news data from database and extract the fields we'd like
  to display
  """
  #top 10 articles
  articles = getArticlesFromDB()[:10]
  # get rid of some fields that we don't need
  top_articles = []

  for art in articles:
    article = {
      'author': art['author'],
      'title': art['title'],
      'description': art['description'],
      'url': art['url'],
      'date': art['date'],
    }
    
    top_articles.append(article)

  return top_articles
  # context['news'] will be updated in query()

  
# Incorporating the Database
def summaryModel() -> str:
  """Using data stored in the database and create a text summary
  """
  textList = [entry['content'] for entry in db['articles']]

  clean_text = cleansText(textList)
  summary = summarize(input_text=clean_text)[0]['summary_text']

  return summary

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080, debug=True)  # runs app