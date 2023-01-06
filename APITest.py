import json
import http.client
import datetime
from constants import *
from replit import db
import os

def makeTwitterRequest(query: str = query) -> dict:
    #In order to allow tweets time to gain popularity, we want our current date to reflect 1 hour prior to the actual current time.
  Current_Date = datetime.datetime.today() - datetime.timedelta(hours=1)
  Previous_Date = Current_Date - datetime.timedelta(seconds=300)
  start_time = Previous_Date.strftime("%Y-%m-%dT%H:%M:%SZ")
  end_time = Current_Date.strftime("%Y-%m-%dT%H:%M:%SZ")
  
# use the http.client library to establish this connection.
  conn = http.client.HTTPSConnection("api.twitter.com")
#  create the information that twitter needs. 
  twitterPayload = ''
  #URLs don't allow spaces, URLs use %20 instead of a space
  query = query.replace(" ", "%20")
  
  #make request 
  conn.request(
  "GET", "/2/tweets/search/recent?query=" + query +
    #-is:retweet means  don't want retweets 
  "%20-is:retweet%20lang:" + language + "&start_time=" + start_time +
  "&end_time=" + end_time + "&max_results=" + str(tweetsPerRequest) +
  "&tweet.fields=author_id,created_at,text,public_metrics",
  twitterPayload, twitterHeaders)
  # Get the response and read it 
  res = conn.getresponse()
  data = res.read()

  # translate it into a python dictionary
  res = {}  #initialize db as a dictionary
  res = json.loads(data.decode("utf-8"))

  # check the response to see if we have any errors, and if we do, print them so we know what they are
  if 'errors' in res:
    for err in res['errors']:
      print(err['message'])

  return res


def newsAPIRequest(query:str) -> dict:
  """
  Makes an api request to newsapi.org.
  Requires:
    query: str - the topic to search
  Returns:
    res: dict - a dictionary containing the response
  """
# Payload: the data that is sent to the server as part of the request message. The payload can include form data, files, or other data that needs to be transmitted to the server.
# Headers: a collection of key-value pairs that are included in the HTTP request message and provide additional information about the request. They can be used to specify various options or preferences for the request, such as the preferred content type, encoding, language, or other HTTP-related details.
# For our request, we will have no payload because we just want to make a request, and our headers will be our API key.
  query = query.replace(' ', '%20')
  fromDate = datetime.datetime.today() - datetime.timedelta(days=7) #fromDate is now set to the current date minus 7 days
  fromDate = fromDate.strftime('%Y-%m-%d') #reformat
  # create an HTTP connection 
  conn = http.client.HTTPSConnection("newsapi.org")
  payload = ''
  headers = { 
    #remember to store your api key in Secrets!
    'Authorization': os.environ['newsapi_apikey'],
    'User-Agent': os.environ['newsapi_apikey']
  }
  conn.request("GET", "/v2/everything?q=" + query +
               "&searchIn=title,description&from=" + fromDate +
               "&sortby=relevancy&language=en", payload, headers)
  #res is an object of type HTTPResponse
  res = conn.getresponse()
  #data is a bytes object that needs to be decoded
  data = res.read()
  #we decode "data" and pass it into json.loads
#res is now a python dictionary
  res = json.loads(data.decode("utf-8"))
  return res


response = newsAPIRequest('Artificial Intelligence')
print(response)