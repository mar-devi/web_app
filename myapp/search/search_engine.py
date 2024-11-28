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
idf = load_pkl_file(path_data + '/idf.pkl')
tf = load_pkl_file(path_data + '/tf.pkl')
index_dic = load_pkl_file(path_data + '/index.pkl')
tweets_popularity = load_pkl_file(path_data + '/tweets_popularity.pkl')
map_docid_tweetid = load_csv_file(path_data + '/tweet_document_ids_map.csv')


def build_demo_results(corpus: dict, search_id):
    """
    Helper method, just to demo the app
    :return: a list of demo docs sorted by ranking
    """
    res = []
    size = len(corpus)
    ll = list(corpus.values())
    for index in range(random.randint(0, 40)):
        item: Document = ll[random.randint(0, size)]
        res.append(ResultItem(item.id, item.title, item.description, item.doc_date,
                              "doc_details?id={}&search_id={}&param2=2".format(item.id, search_id), random.random()))

    # for index, item in enumerate(corpus['Id']):
    #     # DF columns: 'Id' 'Tweet' 'Username' 'Date' 'Hashtags' 'Likes' 'Retweets' 'Url' 'Language'
    #     res.append(DocumentInfo(item.Id, item.Tweet, item.Tweet, item.Date,
    #                             "doc_details?id={}&search_id={}&param2=2".format(item.Id, search_id), random.random()))

    # simulate sort by ranking
    res.sort(key=lambda doc: doc.ranking, reverse=True)
    return res

def build_terms(line, lang):

    stemmer = PorterStemmer()
    stop_words = set(stopwords.words(lang)) # get the stop words for the language

    line = re.sub(r'http\S+', '', line)
    words_line= line.split() # tokenize the text, get a list of terms

    #First we deal with # separation
    treated_words = []
    for word in words_line:

        if word and word[0] == "#":  #If its a hashtag
            separated_list = re.split(r'(?<=[a-z])(?=[A-Z])', word[1:])
            for separated_word in separated_list:
                treated_words.append(separated_word)
        else:
            treated_words.append(word)


    line = [word.lower() for word in treated_words] # everything to lowercase
    translator = str.maketrans('', '', string.punctuation)
    line = [word.translate(translator) for word in line]  # remove punctuation

    line= [word for word in line if word not in stop_words] # remove stop_words
    line= [stemmer.stem(word) for word in line ] # steam
    line = [word for word in line if word.isalnum()]  # keeps only words with alphanumeric characters

    return line

def rank_documents_popularity(terms, docs):# index_dic, idf, tf,tweets_popularity)

    """
    Perform the ranking of the results of a search based on the tf-idf weights

    Argument:
    terms -- list of query terms
    docs -- list of documents, to rank, matching the query
    index -- inverted index data structure
    idf -- inverted document frequencies
    tf -- term frequencies
    title_index -- mapping between page id and page title

    Returns:
    Print the list of ranked documents """

    # I'm interested only on the element of the docVector corresponding to the query terms
    # The remaining elements would become 0 when multiplied to the query_vector
    doc_vectors = defaultdict(lambda: [0] * len(terms)) # I call doc_vectors[k] for a nonexistent key k, the key-value pair (k,[0]*len(terms)) will be automatically added to the dictionary
    query_vector = [0] * len(terms)

    # compute the norm for the query tf
    query_terms_count = collections.Counter(terms)  # get the frequency of each term in the query.
    # Example: collections.Counter(["hello","hello","world"]) --> Counter({'hello': 2, 'world': 1})

    query_norm = la.norm(list(query_terms_count.values()))

    for termIndex, term in enumerate(terms):  #termIndex is the index of the term in the query
        if term not in index_dic:
            continue

    
        query_vector[termIndex] = query_terms_count[term] / query_norm * idf[term]

        # Generate doc_vectors for matching docs
        for doc_index, (doc, doc_positions) in enumerate(index_dic[term]):
          
            if doc in docs:
                doc_vectors[doc][termIndex] = tf[term][doc_index] * idf[term]  # TODO: check if multiply for idf


    #popularity-----
    doc_scores = []
    for doc, curDocVec in doc_vectors.items():

        popularity_score = tweets_popularity[doc]

        cosine_similarity = np.dot(curDocVec, query_vector)

        combined_score = 0.6 * cosine_similarity + 0.4 * popularity_score
        doc_scores.append([doc,combined_score])

    #--------------

   

    doc_scores.sort(reverse=True)

    #result_docs = [x[1] for x in doc_scores] [score,doc_id] ahora es [doc_id,score]!!!
    if len(doc_scores) == 0:
            print("No results found, try again")
 
        

    return doc_scores

def search_in_corpus(corpus,search_id, query):  #index_dic, tf, idf, tweets_popularity,map_docid_tweetid ):
    """
    output is the list of documents that contain any of the query terms.
    So, we will get the list of documents for each query term, and take the union of them.
    """

    query = build_terms(query,'english')
    docs = set()
    i=0
    for term in query:
        try:
            # store in term_docs the ids of the docs that contain "term"
            term_docs = [posting[0] for posting in index_dic[term]]

            if i == 0:
                docs = set(term_docs)
                i = 1
            #docs = docs intersection term_docs
            else: docs &= set(term_docs)

        except:
            #term is not in index
            pass

    docs = list(docs)

    ranked_docs = rank_documents_popularity(query, docs) # index_dic, idf, tf,tweets_popularity)
    #[doc_id,score]


    #tweet_id =  [map_docid_tweetid[key] for key in ranked_docs]
        
    results = []
    for document,score in ranked_docs[:40]:
        results.append(ResultItem(document, corpus[document].title, corpus[document].description, corpus[document].doc_date,
                              "doc_details?id={}&search_id={}&param2=2".format(document, search_id), score)) #cambiar a url
       


    return results


class SearchEngine:
    """educational search engine"""

    def search(self, search_query, search_id, corpus): #, idf,tf,index_dic,tweet_popularity,map_docid_tweetid):
        print("Search query:", search_query)

        ##### your code here #####
        #results = build_demo_results(corpus, search_id)  # replace with call to search algorithm
        
        ##### your code here #####
        #results = search_in_corpus(corpus,search_id,search_query, index_dic, tf, idf, tweet_popularity,map_docid_tweetid)
        results = search_in_corpus(corpus,search_id,search_query)
        
        #take var- #results conatin the numeration of doc
        
        return results
