from flask import Flask, render_template, request
import sys, tweepy, csv
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

@app.route("/")
def main():
    output = ""
    if request.method == 'GET':
        username = request.args.get('username')
        output = username
        
    return render_template('index.html', data= output)

if __name__ == "__main__":
    app.run()