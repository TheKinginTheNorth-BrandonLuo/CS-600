# -*- coding: utf-8 -*-
"""
Created on Tue May  7 07:35:01 2019

@author: FanLuo
"""
import re
import os
from os.path import isfile, join
from bs4 import BeautifulSoup
from os import listdir

urls = [
    'https://en.wikipedia.org/wiki/Marvel_Comics',
    'https://en.wikipedia.org/wiki/Bernoulli',
    'https://en.wikipedia.org/wiki/Hadrian',
    'https://en.wikipedia.org/wiki/Harry_Potter',
    'https://en.wikipedia.org/wiki/King_Arthur',
    'https://en.wikipedia.org/wiki/Lebron_James',
    'https://en.wikipedia.org/wiki/Game_of_Thrones'
    'https://en.wikipedia.org/wiki/Stephen_Curry'
    'https://en.wikipedia.org/wiki/The_Walt_Disney_Company'
]

myPath  = r"E:\CScourses\html"
links = [f for f in listdir(myPath) if isfile(join(myPath, f))]
stopWords = ['a', 'an', 'the', 'in', 'on', 'at', 'he', 'she', 'him', 'her', 'it', 'you', 'I']

def createRank(wordList):
    dictionary = {}
    for word in wordList:
        try:
            dictionary[word] += 1
        except:
            dictionary[word] = 1
    return dictionary

            
def retrieveHtml(link: str):
    html = open(join(myPath, link), 'r', encoding = 'utf-8').read()
    return html
    
def parseText(text: str):#Breaks long strings of text into a list of individual words. Returns a list of the words
    words = re.sub("[^\w]", " ", text.lower()).split()
    words = [word for word in words if word not in stopWords]
    return words

class Node(object):
    def __init__(self, char: str):
        self.char = char
        self.father = None
        self.children = {}
        self.isPrefix = False
        self.isIndexTerm = False
        self.counter = 1
        self.occurenceList = None
        self.rank = None
       

class Trie(object):
    def __init__(self):
        self.root = Node(" ")

    def addWord(self, word: str, link: str, rank: int):
        node = self.root
        for char in word:
            try:
                child = node.children[char]
                child.counter += 1
                node = child
            except:
                newNode = Node(char)
                newNode.father = node
                node.children[char] = newNode
                node = newNode
        node.isIndexTerm = True
        if node.children:
            node.isPrefix = True
        if node.rank:
            try:
                linkRankOld = node.rank[link]
                if linkRankOld != rank:
                    if node.occurenceList:
                        try:
                            linkList = node.occurenceList[linkRankOld]
                            if link in linkList:
                                linkList.remove(link)
                                linkList = node.occurenceList[rank]
                                if link not in linkList:
                                    linkList.append(link)
                        except:
                            node.occurenceList[rank] = [link]
                    else:
                        node.occurenceList = {rank: [link]}
            except:
                node.rank[link] = rank
                if node.occurenceList:
                    try:
                        linkList = node.occurenceList[rank]
                        if link not in linkList:
                            linkList.append(link)
                    except:
                        node.occurenceList[rank] = [link]
        else:
            node.rank = {link: rank}
            if node.occurenceList:
                try:
                    linkList = node.occurenceList[rank]
                    if link not in linkList:
                        linkList.append(link)
                except:
                    node.occurenceList[rank] = [link]
            else:
                node.occurenceList = {rank: [link]}
                

class SearchEngine(object):#Search engine is the main class of the project.
    def __init__(self):
        self.trie = Trie()
        self.compressedTrie = Trie()

    def compressTrie(self):#Compresses the trie to make search more efficient
        node = self.compressedTrie.root
        def compressTrieHelper(node):
            children = list(node.children.values())
            if len(children) == 1 and node.isPrefix == 0:
                child = children[0]
                child.father = None
                del node.father.children[node.char]
                node.char += child.char
                node.father.children[node.char] = node
                node.children = child.children
                node.isPrefix = child.isPrefix
                node.isIndexTerm = child.isIndexTerm
                node.occurenceList = child.occurenceList
                node.rank = child.rank
                compressTrieHelper(node)
            elif len(children) > 1:
                for child in children:
                    compressTrieHelper(child)
        for child in list(node.children.values()):
            compressTrieHelper(child)

            
    def webCrawler(self, trie: Trie, link: str):#Crawls an html document for text to add to the search engine
            pageHtml = retrieveHtml(link)
            pageSoup = BeautifulSoup(pageHtml, 'html.parser')
            pageText = pageSoup.get_text()
            pageWords = parseText(pageText)
            pageRank = createRank(pageWords)
            for word, rank in pageRank.items():
                trie.addWord(word, link, rank)

    def searchWord(self, word: str):
        root = self.compressedTrie.root
        def searchWordHelper(node: Node, string: str):
            children = list(node.children.items())
            for child in children:
                if child[0] == string and child[1].isIndexTerm == 1:
                    return child[1].occurenceList
                elif string.find(child[0]) == 0:
                    return searchWordHelper(child[1], string.replace(child[0], "", 1))
            return  
        return searchWordHelper(root, word)
    
if __name__ == "__main__":
    search_engine = SearchEngine()
    for link in links:
        search_engine.webCrawler(search_engine.compressedTrie, link)
    search_engine.compressTrie()
    print("\n")
    print("Start search\n")
    x = True
    while x:
        search = re.sub("[^\w]", "", input("search ---> ").lower())        
        if search == "q":
            x = False
        else:
            results = search_engine.searchWord(search)
            if results:
                results = sorted(list(results.items()), key = lambda tup: tup[0], reverse = True)
                for tup in results:
                    for result in tup[1]:
                        print(result)
                print("\n")
            else:
                print("None\n")
    print("Error,thank you for searching!")