import json
import http.client
import datetime
from constants import *
from replit import db
import os
import re
import emoji
import requests


# Setting up emoji cleaner 
def give_emoji_free_text(text: str) -> str:
  """
    Removes emoji's from tweets
    Accepts:
        Text (tweets)
    Returns:
        Text (emoji free tweets)
    """
  emoji_list = [c for c in text if c in emoji.EMOJI_DATA]
  clean_text = ' '.join(
    [str for str in text.split() if not any(i in str for i in emoji_list)])
  return clean_text
  

#The function will accept and output a string, so we'll use something called type hints
# unorthodox ':' and 'str' and '-> str:' are type hints.
def url_free_text(text: str) -> str:
  '''
    Removes URL's from tweets
    Accepts:
      Text (tweets)
    Returns:
      Text (Without any urls in it)
    '''
  text = re.sub(r'http\S+', '', text)
  return text

# Removing certain symbols:
def symbol_free_text(text: str) -> str:
  '''
    Cleans text from urls
    '''
  text = re.sub(r'@\S+', '', text)
  text = re.sub(r'#\S+', '', text)
  return text

# Setting up the Profanity cleaner Function
def isProfane(text: str) -> bool:
  """
  Checks if there's profane text in a tweet
  Uses Purgomalum API to check if there's profanity in tweet. 
  Censors profanity using '*' and then counts '*', returning boolean if true.
  
  Accepts:
    Text
  Returns:
    Boolean if there is profanity in text
  """
  response = requests.get(
    f'https://www.purgomalum.com/service/json?text={text}')
  if 'error' in response.json():
    return True
  count_profanity = response.json()['result'].count('*')
  return (count_profanity > 3)

# Making a single Cleaner function
def cleansText(text_list: list) -> str:
  """Given a json in the format of a list, cleans the text of the tweets 
  of urls, emojis, and symbols, preparing it for summerization. Checks for profanity as well. """
  whole_text = 'summarize: '
  for text in text_list:
    temp_text = url_free_text(text)
    temp_text = give_emoji_free_text(temp_text)
    temp_text = symbol_free_text(temp_text)
    if len(temp_text) == 0:
      continue
    if isProfane(temp_text):
      continue
    whole_text += temp_text
  return whole_text

  
def summarize(input_text) -> str:
  """ Summarizes the input text.
  """
  # Gets the token which lets us access API, API url is used to access the model online.
  inf_headers = {"Authorization": f"Bearer {os.environ['inference_api']}"}
  API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

  # Tells us what our input for the model is and what parameters we want. This means we want a relatively small text in the end. 
  query = {
    "inputs": input_text,
    "parameters": {
      "do_sample": False,
      'min_length': 120,
      'max_length': 180
    },
  }
  # Posts the original text to the site and then gets the summary back!
  data = json.dumps(query)
  response = requests.request("POST",
                              API_URL,
                              headers=inf_headers,
                              data=data)
  summary = json.loads(response.content.decode("utf-8"))

  return summary
  
def newsAPIRequest(query: str = query) -> dict:
  """
  Makes an api request to newsapi.org.
  Requires:
    query: str - the topic to search
  Returns:
    res: dict - a dictionary containing the response
  """
  query = query.replace(' ', '%20')
  fromDate = datetime.datetime.today() - datetime.timedelta(days=7)
  fromDate = fromDate.strftime('%Y-%m-%d')
  conn = http.client.HTTPSConnection("newsapi.org")
  payload = ''
  headers = {
    'Authorization': os.environ['newsapi_apikey'],
    'User-Agent': os.environ['newsapi_apikey']
  }
  conn.request(
    "GET", "/v2/everything?q=" + query + "&searchIn=title,description&from=" +
    fromDate + "&sortby=relevancy&language=en", payload, headers)
  res = conn.getresponse()
  data = res.read()
  res = json.loads(data.decode("utf-8"))
  #print(res)
  return res

# will take in the dictionary from our last step, and also the query. We use the query to make sure that an article is acutually pertinent and should be displayed on our webpage

def cleanNewsAPIRes(data:dict, query:str) -> list:
  """
  Cleans the API response dictionary into a list of dictionaries, with each dictionary holding the info for one article. Any articles that do not have the query in the description or title are dropped.
  Requires:
    data: dict - a dictionary of the api response
    query: str - the query of the search
  Returns:
    output: list - a list of dictionaries, each an article
  """
  
  output = []

  for art in data['articles']:
    if (query in art['description']) or (query in art['title']):
      temp = {
      'source': art['source']['name'],
      'author': art['author'],
      'title': art['title'],
      'description': art['description'],
      'url': art['url'],
      'imageLink': art['urlToImage'],
      'date': art['publishedAt'],
      'content': art['content']
      }
      output.append(temp)

  return output


# Sending to database and retrieving from database
def pushArticlesToDB(data: list):
  db['articles'] = data

def getArticlesFromDB() -> list:
  return db['articles']
  
def parseDate(orig: str) -> datetime:
  """
  Takes a formatted time as a str and changes it 
  to a traditional format as a datetime.
  Example result 2022-12-20 18:06:04+00:00.
  """
  res = datetime.datetime.strptime(orig, "%Y-%m-%dT%H:%M:%S.%f%z")
  return res

def makeTwitterRequest(query: str = query) -> dict:
  """
  Makes API request and records response.
  Returns: A string of the API JSON response.
  Note: Use postman to see an example result.
  """

  #edit out latest?

  Current_Date = datetime.datetime.today() - datetime.timedelta(hours=1)
 # inital population
  Previous_Date = datetime.datetime.today() - datetime.timedelta(days=7)
  start_time = Previous_Date.strftime("%Y-%m-%dT%H:%M:%SZ")
  end_time = Current_Date.strftime("%Y-%m-%dT%H:%M:%SZ")

  conn = http.client.HTTPSConnection("api.twitter.com")
  twitterPayload = ''

  query = query.replace(" ", "%20")

  conn.request(
    "GET", "/2/tweets/search/recent?query=" + query +
    "%20-is:retweet%20lang:" + language + "&start_time=" + start_time +
    "&end_time=" + end_time + "&max_results=" + str(tweetsPerRequest) +
    "&tweet.fields=author_id,created_at,lang,text,public_metrics",
    twitterPayload, twitterHeaders)

  res = conn.getresponse()
  data = res.read()
  res = {}  #initialize db as a dictionary
  res = json.loads(data.decode("utf-8"))
  # print error messages if any error happend
  if 'errors' in res:
    for err in res['errors']:
      print(err['message'])

  return res
#response = makeTwitterRequest('Artificial Intelligence') # or just query 
# print the first tweets
# print(response['data'][0])

# The method takes a dictionary that has these values: 'like_count', 'retweet_count', and 'reply_count'. It also takes a list of numerical values, and multiplies those metrics by the first 3 list entries. It calculates the total score by adding all these up, then returns it.
def pointVal(dict: dict, valueList: list = valueList) -> int:
  likeVal = valueList[0]
  #print(likeVal)
  rtVal = valueList[1]
  #print(rtVal)
  replyVal = valueList[2]
  #print(replyVal)

  score = dict['like_count'] * likeVal
  #print('score:' + str(score) )
  score += dict['retweet_count'] * rtVal
  #print('score:' + str(score) )
  score += dict['reply_count'] * replyVal
  #print('score:' + str(score) )
  return score

#Testing how the pointVal function works 
  '''
x  = pointVal({'like_count': 3, 'retweet_count': 2, 'reply_count': 1}, [1, 2, 3])
print (x)
'''
def newsPopulateDB(query: str):
  res = newsAPIRequest(query)
  clean_res = cleanNewsAPIRes(res, query)
  pushArticlesToDB(clean_res)

  return len(clean_res)
  
def tweetsPopulateDB(query:str):
  """
  Make request, clean response.
  Sorts the tweets by popularity score, and updates the top10 data in the database
  if necessary. Pushes all new tweets to the database.
  """
  raw = makeTwitterRequest(query)
  posts = cleanTwitterAPIRes(raw['data'])
  
  for i in range(len(posts)):
    for j in range(0, len(posts) - i - 1):
      if posts[j]['popularity'] < posts[j + 1]['popularity']:
        posts[j], posts[j + 1] = posts[j + 1], posts[j]

  db['top10'] = posts[:10]

  return len(posts)


def cleanTwitterAPIRes(data:dict)->dict:
  posts = []
  for t in data:
    temp = {}
    temp['tweetID'] = t['id']
    temp['text'] = t['text']
    temp['authorID'] = t['author_id']
    temp['date'] = t['created_at']
    temp['retweets'] = t['public_metrics']['retweet_count']
    temp['likes'] = t['public_metrics']['like_count']
    temp['replies'] = t['public_metrics']['reply_count']
    temp['popularity'] = pointVal(t['public_metrics'])
    posts.append(temp)
  return posts










