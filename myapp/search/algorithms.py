import string
from collections import defaultdict
import nltk
nltk.download('stopwords')
import re
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import numpy as np
from numpy import linalg as la
import collections
from myapp.core.utils import load_pkl_file, load_csv_file

from myapp.search.objects import ResultItem 

# Load the precomputed data
idf = load_pkl_file('idf.pkl')
tf = load_pkl_file('tf.pkl')
index_dic = load_pkl_file('index.pkl')
tweets_popularity = load_pkl_file('tweets_popularity.pkl')
map_docid_tweetid = load_csv_file( 'tweet_document_ids_map.csv')


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


def rank_documents_popularity(terms, docs):

    """
    Perform the ranking of the results of a search based on the tf-idf weights

    Argument:
    terms -- list of query terms
    docs -- list of documents, to rank, matching the query

    Returns:
    the list of ranked documents """

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
                doc_vectors[doc][termIndex] = tf[term][doc_index] * idf[term]


    #popularity-----
    doc_scores = []
    for doc, curDocVec in doc_vectors.items():

        popularity_score = tweets_popularity[doc]

        cosine_similarity = np.dot(curDocVec, query_vector)

        combined_score = 0.5 * cosine_similarity + 0.5 * popularity_score
        doc_scores.append([doc,combined_score])

    #--------------

    doc_scores.sort(reverse=True)

    #result_docs = [x[1] for x in doc_scores] [score,doc_id] ahora es [doc_id,score]!!!
    if len(doc_scores) == 0:
            print("No results found, try again")

    return doc_scores


def search_in_corpus(corpus, search_id, query):
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

    ranked_docs = rank_documents_popularity(query, docs)
        
    results = []
    for document,score in ranked_docs:
        results.append(ResultItem(document, corpus[document].title, corpus[document].description, corpus[document].doc_date,
                              "doc_details?id={}&search_id={}&param2=2".format(document, search_id), score)) #cambiar a url
       
    return results
