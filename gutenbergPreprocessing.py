########################################
#  Module: gutenbergPreprocessing.py
#  Author: Shravan Kuchkula
#  Date: 05/24/2019
########################################

import re
import nltk
import string
import requests
from bs4 import BeautifulSoup

def remove_gutenburg_headers(book_text):
    book_text = book_text.replace('\r', '')
    book_text = book_text.replace('\n', ' ')
    start_match = re.search(r'\*{3}\s?START.+?\*{3}', book_text)
    end_match = re.search(r'\*{3}\s?END.+?\*{3}', book_text)
    try:
        book_text = book_text[start_match.span()[1]:end_match.span()[0]]
    except AttributeError:
        print('No match found')    
    return book_text

def remove_gutenberg_footer(book_text):
    if book_text.find('End of the Project Gutenberg') != -1:
        book_text = book_text[:book_text.find('End of the Project Gutenberg')]
    elif book_text.find('End of Project Gutenberg') != -1:
        book_text = book_text[:book_text.find('End of Project Gutenberg')]
    return book_text

def getTextFromURLByRemovingHeaders(book_urls):
    book_texts = []
    for url in book_urls:
        book_text = requests.get(url).text
        book_text = remove_gutenburg_headers(book_text)
        book_texts.append(remove_gutenberg_footer(book_text))
    return book_texts

def searchPossibleStarts(pattern, book):
    match = re.search(pattern, book, flags=re.IGNORECASE)
    if match:
        return match.span()[0]
    return -1

def moveToStartOfTheBook(possible_starts, book):
    # construct start indexes
    start_indexes = [searchPossibleStarts(ps, book) for ps in possible_starts]
    
    # calculate the lowest index of the list of possible values. Use that as the start index.
    # TODO: this throws an exception when nothing is found
    min_index = min(list(filter(lambda x: x != -1, start_indexes)))
    
    if min_index > -1:
        return book[min_index:]
    else:
        print("Match not found in possible_starts, update your possible_starts")
    
    return book