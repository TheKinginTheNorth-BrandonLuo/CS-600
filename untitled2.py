# -*- coding: utf-8 -*-
"""
Created on Tue May  7 07:35:46 2019

@author: dell
"""

import datetime
import requests

from nltk.corpus import stopwords
from collections import Counter
from boilerpipe.extract import Extractor
from bs4 import BeautifulSoup
from goose import Goose

# Function to scrape RSS feed for text data, used to get text documents

def scrape(feed, used, excep, split1, split2, urlName, nameF):
	arrLinks = []
	req = requests.get('http://feeds.reuters.com/reuters/businessNews')
	soupRss = BeautifulSoup(req.text, "html5lib")

	logrFile = open(used,"r")
	usedLinks = [line.strip() for line in logrFile]
	logrFile.close()

	for link in soupRss.find_all('guid'):
		arrLinks.append(str(link.getText().replace('?feedType=RSS&feedName=businessNews', '')))

	log_file = open(used,"w")
	for item in arrLinks:
		log_file.write(str(item)+"\n")
	log_file.close()

	for i in range(0, 8):
		fileName = arrLinks[i].rsplit('/', split1)[split2]
		#if any(fileName in s for s in usedLinks):
		#	print fileName +" has been extracted."
		#else:
		extractedText = Extractor(extractor='ArticleExtractor', url=urlName+fileName)
		print fileName
		write_file = open("Data/"+str(i)+".txt","w")
		write_file.write(str(datetime.date.today()) + "\n")
		write_file.write(str(extractedText.getText().encode("utf-8")))
		write_file.close()


# Function that outputs occurrence lists
def textCount(data):
	# Create list of characters to delete
	charDel = [".",",","/","?","<",">",":",";","[","]","{","}","-",
	"_","+","=","|",'"',"!","@","#","$","%","^","&","*","(",")"]
	for char in charDel:
		data = data.replace(char,"")
	numDel = list(range(10))
	for num in numDel:
		data = data.replace(str(num),"")
	# Splits data into a list
	datAr = data.split()
	# Creates a list of stopwords to delete using the NLTK library
	stopDel = list(str(stopwords.words('english')))
	# Adding extra words not covered above
	ex = ["the", "The", "to","and", "of", "for", "is"]
	for w in ex:
		stopDel.append(w)
	for word in datAr:
		if word in stopDel:
			datAr.remove(word)
	# Uses Counter to make an occurrence list which is stored in a dictionary
	counts = Counter(datAr)
	index_terms = counts.items()
	return index_terms
# Function to create a trie using a list of words
end = 'last'
def create_trie(words):
	root = {}
	ind = 0
	for word in words:
		current_dict = root
		for letter in word:
			current_dict = current_dict.setdefault(letter, {})
		current_dict[end] = ind
		ind = ind + 1
	return root
# Function to find and return the index value from a trie
def test_trie(trie, word):
	current_dict = trie
	for letter in word:
		if letter in current_dict:
			current_dict = current_dict[letter]
		else:
			return 0
	else:
		if end in current_dict:
			return current_dict[end]
		else:
			return 0

# Function that gets tries from all 8 sources
trie = []
indexTerms = []
def trieForm():
	for i in range(0,8):
		# Opens Text file with text from a scraped webpage
		file = "Data/"+(str(i)) + ".txt"
		logr_file = open(file)
		dt = logr_file.read()
		logr_file.close()
		# returns text count
		iterms = textCount(dt)
		indexTerms.append(textCount(dt))
		# creates list of words from the dictionary to make a trie out of
		wordList=[]
		for w in iterms:
			wordList.append(w[0])
		trie.append(create_trie(wordList))
#Creates tries and occurance lists for each webpage
trieForm()
# creates the rank list for searching
rank = []
def search(term, fileOut):
	# create temp list to split search term into
	temp = []
	temp = term.split()
	if fileOut:
		print >> f,"Search terms:"
		print >> f, temp
	else:
		print("Search terms:")
		print(temp)

	# iterate through every trie
	for i in range(0,8):
		sum = 0
		#iterate through every search term
		for t in temp:
			# If search finds the term, it adds the occurrences to the rank
			if test_trie(trie[i], t) > 0:
				# Uses index at the bottom of trie to find number of occurrences in the index terms
				sum = sum + int(indexTerms[i][test_trie(trie[i], t)][1])
		rank.append(sum)
	return rank

menu = True
while menu:
	print ("""
	1. Extract News
	2. Read to Text File
	3. Read to Console
	4. Exit/Quit
	""")
	menu = raw_input("Enter input: ") 
	if menu == "1": 
		scrape("http://feeds.reuters.com/reuters/businessNews","usedReuter.txt",'http://www.reuters.com',1,-1,"http://www.reuters.com/article/","reuters_")
	elif menu == "2":
		f = open('test3.txt', 'w')
		#Test the search terms to return the ranks from the search
		test = search("Boston cities dollar", True)
		# Iterate through the ranks and output
		best = [None, 0]
		for it in range(0,8):
			print >> f, "Webpage " + str(it) + " rank:"
			print >> f, test[it]
			if best[1] < test[it]:
				best[0] = it
		if best[0] == None:
			print >> f, "Search result not found in any of the webpages."
		else:
			print >> f, "Highest ranking search from Webpage " + str(best[0])
		print >> f, "\n"
		print >> f, "Index Terms Output"
		for j in range(0, 8):
			print >> f, "Webpage " + str(j)
			print >> f, indexTerms[j]
		print >> f, "\n"
		print >> f, "Tries Output"
		for k in range(0, 7):
			print >> f, "Webpage " + str(k)
			print >> f, trie[k]
		f.close()
	elif menu == "3":
		test = search("Boston cities dollar", False)
		# Iterate through the ranks and output
		best = [None, 0]
		for it in range(0,8):
			print("Webpage " + str(it) + " rank:")
			print(test[it])
			if best[1] < test[it]:
				best[0] = it
		if best[0] == None:
			print("Search result not found in any of the webpages.")
		else:
			print("Highest ranking search from Webpage " + str(best[0]))
		print("\n")
		print("Index Terms Output")
		for j in range(0, 8):
			print("Webpage " + str(j))
			print(indexTerms[j])
		print("\n Tries Output")
		for k in range(0, 7):
			print("Webpage " + str(k))
			print(trie[k])
	elif menu == "4":
		print("Goodbye")
		menu = False 
	elif menu != "":
		print("\n Not Valid Choice Try again") 