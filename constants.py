import os
bearer_token = os.environ['bearer_token']
guest_id = os.environ['tGuest']
#print('code works')
twitterHeaders = {
  'Authorization': 'Bearer ' + bearer_token,
  'Cookie': 'guest_id=' + guest_id 
}
#set default value for query
query = "artificial intelligence"
# set language to Enlish 
language = 'en'
# set how many tweets we want  
tweetsPerRequest = 100

# make a method that gives each tweet a "popularity score" based on how many likes, retweets, and replies it has
# This sets the default value of a like, a retweet, and a reply to a tweet's popularity score
valueList = [1, 3, 5]
