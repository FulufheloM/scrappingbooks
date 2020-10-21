import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
import nltk
import string
import matplotlib.pyplot as plt
import seaborn as sns
from scrapeGutenberg import *
from gutenbergPreprocessing import *
from gutenbergTextNormalization import *

# bookshelf url
bookshelf = 'http://www.gutenberg.org/wiki/Children%27s_Instructional_Books_(Bookshelf)'

# from the bookshelf get all the book_urls, titles, 
# authors and soup(for getting categories)
book_urls, titles, authors, soup = getBookURLsFromBookShelf(bookshelf)

# construct a books dataframe
books = pd.DataFrame({'url': book_urls, 'title': titles, 'author(s)': authors})

# get books df with categories
books = getCategories(soup, books)

# with categories
display(books.shape)
books.head()

# get the book urls from the dataframe
book_urls = list(books.url.values)

# keep only text between *START* and *END* 
book_texts = getTextFromURLByRemovingHeaders(book_urls)

# list of regular expressions of possible starts
possible_starts = [r'INTRODUCTION', r'\[?ILLUSTRATION', r'CONTENTS', r'IMPRUDENCE', r'TABLE DES MATI',
                  r'THE ALPHABET', r'SELECTIONS IN PROSE AND POETRY', r'THE PLAN BOOK SERIES', 
                  r'STORIES FROM LIVY', r'CHAPTER ONE', r'POEMS TEACHERS ASK FOR', r'OP WEG NAAR SCHOOL.',
                  r'HOW TO USE THE BOOK']

# iterate over the list of possible starts and find the best starting point
book_texts = [moveToStartOfTheBook(possible_starts, book) for book in book_texts]

clean_books = cleanTextBooks(book_texts)

normalizedVocab = normalizedVocabularyScore(clean_books)
summary = pd.concat([books, normalizedVocab], axis=1)