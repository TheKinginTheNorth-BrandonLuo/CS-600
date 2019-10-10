from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
from os import listdir
from os.path import isfile, join
myPath  = r"E:\CScourses\html"
links = [f for f in listdir(myPath) if isfile(join(myPath, f))]

stopWords = ['ourselves', 'hers', 'between', 'yourself', 'but', 'again', 'there', 'about', 'once', 'during', 'out', 'very', 'having', 'with', 'they', 'own', 'an', 'be', 'some', 'for', 'do', 'its', 'yours', 'such', 'into', 'of', 'most', 'itself', 'other', 'off', 'is', 's', 'am', 'or', 'who', 'as', 'from', 'him', 'each', 'the', 'themselves', 'until', 'below', 'are', 'we', 'these', 'your', 'his', 'through', 'don', 'nor', 'me', 'were', 'her', 'more', 'himself', 'this', 'down', 'should', 'our', 'their', 'while', 'above', 'both', 'up', 'to', 'ours', 'had', 'she', 'all', 'no', 'when', 'at', 'any', 'before', 'them', 'same', 'and', 'been', 'have', 'in', 'will', 'on', 'does', 'yourselves', 'then', 'that', 'because', 'what', 'over', 'why', 'so', 'can', 'did', 'not', 'now', 'under', 'he', 'you', 'herself', 'has', 'just', 'where', 'too', 'only', 'myself', 'which', 'those', 'i', 'after', 'few', 'whom', 't', 'being', 'if', 'theirs', 'my', 'against', 'a', 'by', 'doing', 'it', 'how', 'further', 'was', 'here', 'than']
def retrieHtml(link:str):
    html = open(join(mypath,link) , 'r' ,encoding ='utf-8').read()
    return html

def parseText(text:str):
    words = re.sub("[^\w]", " ", text.lower()).split()
    words = [word for word in words if word not in stopWords]
    return words

def createRank(wordList):
    dictionary = {}
    for word in wordList:
        try:
            dictionary[word] += 1
        except:
            dictionary[word] = 1
    return dictionary

class Node(object):
    def _init_(self, char:str):
        self.char = char
        self.parent = None
        self.children = {}
        self.isPrefix = False
        self.isIndexTerm = False
        self.counter = 1
        self.occurenceList = None
        self.rank = None

    def _str_(self):
        return """Node:\tchar: "%s",
\tchildren: %s
\tisPrefix: %s
\tisIndexTerm: %s
\tcounter: %s
\toccureneceList: %s
\trank: %s""" % (self.char, self.children, self.isPrefix, self.isIndexTerm, self.counter, self.occurenceList, self.rank)

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
                newNode.parent = node
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

class SearchEngine(object):
    def __init__(self):
        self.trie = Trie()
        self.compressedTrie = Trie()
    
    def crawlPage(self, trie: Trie, link: str):
        pageHtml = retrieveHtml(link)
        pageSoup = BeautifulSoup(pageHtml, 'html.parser')
        pageText = pageSoup.get_text()
        pageWords = parseText(pageText)
        pageRank = createRank(pageWords)
        for word, rank in pageRank.items():
            trie.addWord(word, link, rank)

    def compressTrie(self):
        node = self.compressedTrie.root
        def compressTrieHelper(node):
            children = list(node.children.values())
            if len(children) == 1 and node.isPrefix == 0:
                child = children[0]
                child.parent = None
                del node.parent.children[node.char]
                node.char += child.char
                node.parent.children[node.char] = node
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

    def searchWord(self, word: str):
        root = self.compressedTrie.root
        def searchWordHelper(node: Node, string: str):
            children = list(node.children.items())
            for child in children:
                if child[0] == string and child[1].isIndexTerm == 1:
                    return child[1].occurenceList
                elif string.find(child[0]) == 0:
                    return searchWordHelper(child[1], string.replace(child[0], "", 1))
            return None
        return searchWordHelper(root, word)

if __name__ == "__main__":
    SE = SearchEngine()
    for link in links:
        SE.crawlPage(SE.compressedTrie, link)
    SE.compressTrie()
    print("\n")
    print("Let's start search!\n")
    x = True
    while x:
        search = re.sub("[^\w]", "", input("search -> ").lower())        
        if search == "q":
            x = False
        else:
            results = SE.searchWord(search)
            if results:
                results = sorted(list(results.items()), key = lambda tup: tup[0], reverse = True)
                for tup in results:
                    for result in tup[1]:
                        print(result)
                print("\n")
            else:
                print("None\n")
    print("Thanks for searching!")