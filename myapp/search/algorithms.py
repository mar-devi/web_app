import random
import string
from collections import defaultdict, Counter
from array import array
import nltk
nltk.download('stopwords')
import re
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import math
import numpy as np
import pandas as pd
from numpy import linalg as la
import matplotlib.pyplot as plt
import collections
from myapp.core.utils import load_pkl_file, load_csv_file
import os

from myapp.search.objects import ResultItem, Document


path_data = '/Users/uni/Documents/4upf/1trim/IR/final part/search-engine-web-app-main' + '/data'
idf = load_pkl_file('idf.pkl')
tf = load_pkl_file('tf.pkl')
index_dic = load_pkl_file('index.pkl')
tweets_popularity = load_pkl_file('tweets_popularity.pkl')
map_docid_tweetid = load_csv_file( 'tweet_document_ids_map.csv')

def search_in_corpus(query):
    # 1. create create_tfidf_index


    # 2. apply ranking

    
    return ""
