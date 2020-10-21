########################################
#  Module: gutenbergTextNormalization.py
#  Author: Shravan Kuchkula
#  Date: 05/24/2019
########################################

import re
import pandas as pd
import numpy as np
import nltk
import string
from nltk.stem import LancasterStemmer
from nltk.stem import WordNetLemmatizer

# tokenize text
def tokenize_text(book_text):
    TOKEN_PATTERN = r'\s+'
    regex_wt = nltk.RegexpTokenizer(pattern=TOKEN_PATTERN, gaps=True)
    word_tokens = regex_wt.tokenize(book_text)
    return word_tokens

def remove_characters_after_tokenization(tokens):
    pattern = re.compile('[{}]'.format(re.escape(string.punctuation))) 
    filtered_tokens = filter(None, [pattern.sub('', token) for token in tokens]) 
    return filtered_tokens

def convert_to_lowercase(tokens):
    return [token.lower() for token in tokens if token.isalpha()]

def remove_stopwords(tokens):
    stopword_list = nltk.corpus.stopwords.words('english')
    filtered_tokens = [token for token in tokens if token not in stopword_list]
    return filtered_tokens

def apply_stemming_and_lemmatize(tokens, ls=LancasterStemmer(), wnl=WordNetLemmatizer()):
    return [wnl.lemmatize(ls.stem(token)) for token in tokens]

def cleanTextBooks(book_texts):
    clean_books = []
    for book in book_texts:
        book_i = tokenize_text(book)
        book_i = remove_characters_after_tokenization(book_i)
        book_i = convert_to_lowercase(book_i)
        book_i = remove_stopwords(book_i)
        book_i = apply_stemming_and_lemmatize(book_i)
        clean_books.append(book_i)
    return clean_books

def normalizedVocabularyScore(clean_books):
    v_size = [len(set(book)) for book in clean_books]
    max_v_size = np.max(v_size)
    v_raw_score = v_size/max_v_size
    v_sqrt_score = np.sqrt(v_raw_score)
    v_rank_score = pd.Series(v_size).rank()/len(v_size)
    v_final_score = (pd.Series(v_sqrt_score) + v_rank_score)/2
    
    return pd.DataFrame({'v_size': v_size,
                        'v_raw_score': v_raw_score,
                        'v_sqrt_score': v_sqrt_score,
                        'v_rank_score': v_rank_score,
                        'v_final_score': v_final_score})

def longWordVocabularySize(clean_book, minChar=10):
    V = set(clean_book)
    long_words = [w for w in V if len(w) > minChar]
    return len(long_words)

def normalizedLongWordVocabularyScore(clean_books):
    lw_v_size = [longWordVocabularySize(book) for book in clean_books]
    max_v_size = np.max(lw_v_size)
    v_raw_score = lw_v_size/max_v_size
    v_sqrt_score = np.sqrt(v_raw_score)
    v_rank_score = pd.Series(lw_v_size).rank()/len(lw_v_size)
    lw_v_final_score = (pd.Series(v_sqrt_score) + v_rank_score)/2
    
    return pd.DataFrame({'lw_v_size': lw_v_size,
                        'lw_v_final_score': lw_v_final_score})


def textDifficultyScore(clean_books):
    df_vocab_scores = normalizedVocabularyScore(clean_books)
    df_lw_vocab_scores = normalizedLongWordVocabularyScore(clean_books)
    lexical_diversity_scores = [len(set(book))/len(book) for book in clean_books]
    
    text_difficulty = (df_vocab_scores['v_final_score'] + \
                     df_lw_vocab_scores['lw_v_final_score'] + \
                     lexical_diversity_scores)/3
    
    return pd.DataFrame({'text_difficulty': text_difficulty})