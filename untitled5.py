# -*- coding: utf-8 -*-
"""
Created on Wed May  8 11:03:04 2019

@author: dell
"""

from __future__ import print_function

import os
import traceback
from tqdm import tqdm
from inverted_index import InvertedIndex
from web_crawler import WebCrawler

urls = [
    'https://en.wikipedia.org/wiki/Game_of_Thrones',
    'https://en.wikipedia.org/wiki/Alan_Turing',
    'https://en.wikipedia.org/wiki/Avengers:_Endgame',
    'https://en.wikipedia.org/wiki/Friends',
    'https://en.wikipedia.org/wiki/Machine_learning',
    'https://en.wikipedia.org/wiki/Michael_Jordan',
    'https://en.wikipedia.org/wiki/Beijing'
]

class SearchEngine(object):
    ''' SearchEngine is the main class of this system.
        Methods:
            add_page() -- Add a new html files in the file system of OS.
            search() -- Search key word in the system, return all the url and file contain this word.
        Attributes:
            inverted_index -- The data structure maintains all the terms and the coorespending URL/File
            crawler -- A object that parsing html format input to raw text, 
                       and then preprocess the raw text into a array of words which can save into inverted_index.
    '''

    def __init__(self):
        self.inverted_index = InvertedIndex()
        self.crawler = WebCrawler()

    def add_page(self, page):
        if page.startswith('http'): ## if input with http, it is a url, otherwise if a file path
            pass
            words = self.crawler.add_url(page)
            self.inverted_index.add(page, words)
        else:
            words = self.crawler.add_pages(page)
            self.inverted_index.add(page, words)
            print()
            self.inverted_index.print_trie()

    def search(self, word):
        outs = self.inverted_index.search(word)
        if outs:
            print('Searching key word is {}'.format(word))
            for i,out in enumerate(outs):
                print('{}. {}'.format(i+1, out))
            print()
        else:
            print('Can not find key {} in SearchEngine.\n'.format(word))

    def print_trie(self):
        self.inverted_index.print_trie()
        

if __name__ == "__main__":
    print('----- Welcome the SearchEngine (CS600 project). Powered by Kun Wu. ----')
    print('##### Commands ######')
    print('Input a or add [file_path] url] to add new html file or URL to the sys, e.g. add ./pages/Alan_Turing.html')
    print('Input s or search [key_word] to search the key word in the system, return the documents contains this word')
    print('#####################')
    print('')

    search_engine = SearchEngine()
    
    while True:
        input_text = input('Type your command:')
        try:
            ## validate the input
            args = input_text.strip().split(' ')
            if len(args) == 1:
                command = args[0]
            elif len(args) == 2:
                command = args[0]
                parameter = args[1]
            else:
                print('Oops, invalid input. Please input again.\n')
                continue
            
            ## handle the input command
            if command.lower() == 'q' or command.lower() =='quit':
                break
            elif command.lower() == 'a' or command.lower() == 'add':
                print('Adding new page {} to the system.\n'.format(parameter))
                search_engine.add_page(parameter)
            elif command.lower() == 's' or command.lower() == 'search':
                search_engine.search(parameter)
            elif command.lower() == 'd' or command.lower() == 'default':
                print('loading pre-saved urls, ', urls)
                for url in tqdm(urls):
                    search_engine.add_page(url)
                print()
            elif command.lower() == 'p' or command.lower() == 'print': ## Debug command
                search_engine.print_trie()
            else:
                print('Unsupported command, please input correct command.\n')

        except Exception as err:
            print('Oops... Unexpected error: {}. \n'.format(err))
            traceback.print_exc()
            continue

    print('Quiting... Thanks to use SearchEngine.\n')
