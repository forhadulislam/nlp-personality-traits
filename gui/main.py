from flask import Flask, render_template, request
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
auth.set_access_token("375649778-Kl3GcRRyxX3Lratuy0VWtzSA8zR5ChQCQf0CfqDq", "2zeUm5CdduuaAYUM9RZ5almqryZVwqK3DCFHuCtvky0R7")
api = tweepy.API(auth)

app = Flask(__name__)


# Loading the model
model = gensim.models.KeyedVectors.load_word2vec_format('../../GoogleNews-vectors-negative300.bin.gz', limit=1000000, binary=True)

'''
    Creating a dictionary all of the traits 
'''
pTraits = ['extraversion','neuroticism', 'agreeableness','conscientiousness','openness']
allTraits = {}
allTraitsScore = {}

for traits in pTraits:
    allTraitsScore[traits] = 0

with open('../wordsassociatedwithdifferenttraits.csv', 'rb') as f:
    next(f)
    reader = csv.reader(f)    
    for row in reader:
        for index, data in enumerate(row):
            cKey = pTraits[index - 1]
            rowKey = row[0]
            if index != 0:
                cVal = float(data)
                if cVal:
                    if cKey in allTraits:
                        allTraits[pTraits[index - 1]][rowKey] = cVal
                    else:
                        allTraits[pTraits[index - 1]] = {}
                        allTraits[pTraits[index - 1]][rowKey] = cVal
 
    f.close()

alltweets = []

@app.route("/")
def main():
	output = profileImage = ""
	finalOutput = {}
	if request.method == 'GET':
		username = request.args.get('username')
		if username:
			new_tweets = api.user_timeline(screen_name = username,count=200) 
			alltweets.extend(new_tweets)
			
			profileImage = new_tweets[0].user.profile_image_url_https
			
			# Save the id of the last tweet fetched
			last = alltweets[-1].id - 1
			while ((len(alltweets) < 5000) & (len(new_tweets)> 0)): #keep fetching tweets till we get 1000 tweets or reach the end of the timeline
					
				new_tweets = api.user_timeline(screen_name = username,count=200,max_id=last)
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

			thefile = open( username + '.txt', 'w')
			thefile.write("%s\n" % outtweets)


			tokens = word_tokenize(outtweets)
			wordFreq = FreqDist(tokens)

			# Taking most frequent words 
			mostCommonWords = wordFreq.most_common(500)


			output = {}

			#looping through all traights and creating the output dictionary

			for traits in allTraits:
				currentTraits = traits
				
				output[currentTraits]= {}
				output[currentTraits] = {}
					
				output[currentTraits]["positive"] = []
				output[currentTraits]["negative"] = []

			cosSim = 0

			for word in mostCommonWords:
				totalFreqWords = len(mostCommonWords)
				currentWord = word[0]
				
				
				for traits in allTraits:
					currentTraits = traits
					currentTraitsKeywords = allTraits[traits]
					currentTraitsValue = 0
					currentTraitsKeywordsLength = len(currentTraitsKeywords)
					
					
					
					for cWords in currentTraitsKeywords:
						# cWords is the current word from allTraits
						# cWordsCoeff is the coefficient of the word
						cWordsCoeff = allTraits[traits][cWords]
						
						# claculating cosine similarity
						currentWord = currentWord.strip()
						cWords = cWords.strip()
						try:
							cosine_similarity = np.dot( model[currentWord], model[cWords] ) / ( np.linalg.norm( model[currentWord] ) * np.linalg.norm( model[cWords] ) )
						except:
							cosine_similarity = 0
						
						if cosSim > cosine_similarity:
							cosSim = cosine_similarity
						
						#print(cWordsCoeff)
						
						if cWordsCoeff > 0:
							opS = cWordsCoeff * cosine_similarity
							output[currentTraits]["positive"].append( str(opS) )
						else:
							opS = abs(cWordsCoeff) * cosine_similarity
							output[currentTraits]["negative"].append( str(opS) )


			for ab in output:
				
				
				positiveValue = negativeValue = float(0)
				
				for pVal in output[ab]["positive"]:
					positiveValue += float(pVal)
					
				for nVal in output[ab]["negative"]:
					negativeValue += float(nVal)
					
				positiveOutput = positiveValue / len(output[ab]["positive"])
				negativeOutput = negativeValue / len(output[ab]["negative"])
				
				pTraitsValue = 3*((8.0 * ( ((positiveOutput - negativeOutput)) + abs(cosSim) ) / abs(cosSim) ) - 6)
				
				finalOutput[ab] = pTraitsValue



	return render_template('index.html', user= username, finalOutput= finalOutput, profileImage= profileImage)

if __name__ == "__main__":
	app.run()
