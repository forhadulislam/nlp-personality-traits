import sys, tweepy, csv, gensim
import numpy as np
import re, string, timeit
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer

stop = set(stopwords.words('english'))
punctuation = ['(', ')', '?', ':', ';', ',', '.', '!', '/', '"', "'"] 

# Twitter API 
auth = tweepy.OAuthHandler(	"8oLwBKMlnVw1Ezv9C4HWl5zsq", "njjiIBuVCgjeiTTmKHqFKk5wbMLRa48OkgQgqYqfVYmhVnp8LP")
auth.set_access_token(	"375649778-Kl3GcRRyxX3Lratuy0VWtzSA8zR5ChQCQf0CfqDq", "2zeUm5CdduuaAYUM9RZ5almqryZVwqK3DCFHuCtvky0R7")
api = tweepy.API(auth)

 

alltweets = [] #a list to aggregate all of the tweets fetched

#Requesting the first 200 tweets
screen_name = "TheEllenShow" 
new_tweets = api.user_timeline(screen_name = screen_name,count=200) 
alltweets.extend(new_tweets)



print( jsonStatus )

exit()

# Save the id of the last tweet fetched
last = alltweets[-1].id - 1
while ((len(alltweets) < 5000) & (len(new_tweets)> 0)): #keep fetching tweets till we get 1000 tweets or reach the end of the timeline
		
	new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=last)
	alltweets.extend(new_tweets)
	last = alltweets[-1].id - 1
    

processedTweets = []

porter_stemmer = PorterStemmer()

for cTweet in alltweets:
	
	tweetText = cTweet.text.encode("utf-8")
	
	# Stripping the URLs    
	tweetText = re.sub(r"(?:\@|https?\://)\S+", "", tweetText, flags=re.MULTILINE)    
	# Removing HASH
	tweetText = re.sub(r'#\w+ ?', '', tweetText)
	# Removing the Hex characters
	tweetText = re.sub(r'[^\x00-\x7f]',r'', tweetText)

	# removing puntuations
	tweetText = re.sub(r'[^a-zA-Z0-9\s]', ' ', tweetText)


	sWordRemovedTweet = [i for i in word_tokenize(tweetText.lower()) if i not in stop]
	cleanedTweet = ' '.join(sWordRemovedTweet)

	#print(cleanedTweet)

	processedTweets.append(cleanedTweet)
    
outtweets = ''
for tweet in processedTweets:
    outtweets += tweet

thefile = open( screen_name + '.txt', 'w')
thefile.write("%s\n" % outtweets)
