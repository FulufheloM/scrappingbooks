##############################
#  Module: scrapeGutenberg.py
#  Author: Shravan Kuchkula
#  Date: 05/24/2019
##############################

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np


def getTitlesAndAuthors(title_and_authors):
    titles = []
    authors = []
    for ta in title_and_authors:
        titles.append(ta[0])
        authors.append(ta[1])
    return titles, authors

def getBookURLsFromBookShelf(bookshelf):
    
    # make a request and get a response object
    response = requests.get(bookshelf)
    
    # get the source from the response object
    source = response.text
    
    # construct the soup object
    soup = BeautifulSoup(source, 'html.parser')
    
    # get all the a tags
    tags = soup.find_all('a', attrs={'class': 'extiw'})
    
    # get all the urls
    urls = ["http:" + tag.attrs['href'] for tag in tags]
    
    # construct the soup
    soups = [BeautifulSoup(requests.get(url).text, 'html.parser') for url in urls]
    
    # get all the plain text files
    href_tags = [soup.find(href=True, text='Plain Text UTF-8') for soup in soups]

    # get all the book urls
    book_urls = ["http:" + tag.attrs['href'] for tag in href_tags]
    
    # get h1 tags for getting titles and authors
    h1_tags = [soup.find('h1').getText() for soup in soups]
    
    # construct titles and authors list
    title_and_authors = [re.split(r'by', tag) for tag in h1_tags]

    # some titles don't have authors, so add Unknown to author
    for ta in title_and_authors:
        if len(ta) == 1:
            ta.append("Unknown")
    
    # get the titles and authors into their own lists
    titles, authors = getTitlesAndAuthors(title_and_authors)
    
    return book_urls, titles, authors, soup

def getCategories(soup, books):
    # get all the tags
    tags = soup.find_all('a', attrs={'class': 'extiw'})

    # get all the titles
    title_id = [tag.attrs['title'] for tag in tags]

    # clean the title
    title_ids = [title.split(':')[1] for title in title_id]

    # create a new column
    books['title_id'] = title_ids

    # create a categories column
    books['category'] = ""

    # get the categories from h3 tags
    for h3 in soup.find_all('h3'):
        #print(h3.getText())
        category = h3.getText()
        h3_atags = h3.findNextSibling().find_all('a', attrs={'class': 'extiw'})
        for tag in h3_atags:
            #print(tag['title'].split(':')[1])
            book_id = tag['title'].split(':')[1]
            books['category'].iloc[np.where(books.title_id == book_id)] = category

    # get the categories from h2 tags
    for tag in soup.find_all('h2'):
        if len(tag.findChildren()) > 0:
            for t in tag.children:
                if t.getText() != 'Readers' and t.getText() != 'Uncategorized':
                    #print(t.getText())
                    category = t.getText()
                    h2_atags = tag.findNextSibling().find_all('a', attrs={'class': 'extiw'})
                    for atag in h2_atags:
                        book_id = atag['title'].split(':')[1]
                        books['category'].iloc[np.where(books.title_id == book_id)] = category

    # remaining links are uncategorized
    books['category'].iloc[np.where(books.category == '')] = 'Uncategorized'
    
    return books