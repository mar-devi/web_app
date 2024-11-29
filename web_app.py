import os
from json import JSONEncoder

# pip install httpagentparser
import httpagentparser  # for getting the user agent as json
import nltk
from flask import Flask, render_template, session
from flask import request

from myapp.analytics.analytics_data import AnalyticsData, ClickedDoc
from myapp.search.load_corpus import load_corpus
from myapp.search.objects import Document, StatsDocument
from myapp.search.search_engine import SearchEngine
from myapp.core.utils import load_pkl_file, load_csv_file

from flask import redirect, url_for
import requests
from datetime import datetime
import json


# *** for using method to_json in objects ***
def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)


_default.default = JSONEncoder().default
JSONEncoder.default = _default

# end lines ***for using method to_json in objects ***

# instantiate the Flask application
app = Flask(__name__)

# random 'secret_key' is used for persisting data in secure cookie
app.secret_key = 'afgsreg86sr897b6st8b76va8er76fcs6g8d7'
# open browser dev tool to see the cookies
app.session_cookie_name = 'IRWA_SEARCH_ENGINE'

# instantiate our search engine
search_engine = SearchEngine()

# instantiate our in memory persistence
analytics_data = AnalyticsData()

# print("current dir", os.getcwd() + "\n")
# print("__file__", __file__ + "\n")
full_path = os.path.realpath(__file__)
path, filename = os.path.split(full_path)
# print(path + ' --> ' + filename + "\n")
# load documents corpus into memory.
file_path = path + "/data/farmers-protest-tweets.json.gz"

# file_path = "../../tweets-data-who.json"
corpus = load_corpus(file_path)
#print("loaded corpus. first elem:", list(corpus.values())[0])

print("loaded corpus. first elem:", list(corpus.values())[0])
map_docid_tweetid = load_csv_file( 'tweet_document_ids_map.csv')



def get_public_ip():
    try:
        response = requests.get('https://api64.ipify.org?format=json')
        return response.json()['ip']
    except Exception as e:
        print(f"Error fetching public IP: {e}")
        return "Unknown"

def get_country_city(ip_address):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}")
        js = response.json()

        if js['status'] == 'fail':
            return {"country": "Unknown", "city": "Unknown"}
        
        country = js.get('country', 'Unknown')
        city = js.get('city', 'Unknown')

        return country, city

    except Exception as e:
        return {"country": "Unknown", "city": "Unknown"}

def get_country_and_city2(ip_address):
    try:
        response = requests.get(f'https://ipinfo.io/{ip_address}/json')
        data = response.json()
        country = data.get('country', 'Unknown')
        city = data.get('city', 'Unknown')
        return country, city
    except Exception as e:
        return "Unknown", "Unknown"


# Home URL "/"
@app.route('/')
def index():
    print("starting home url /...")

    # flask server creates a session by persisting a cookie in the user's browser.
    # the 'session' object keeps data between multiple requests
    session['some_var'] = "IRWA 2021 home"

    user_agent = request.headers.get('User-Agent')
    print("Raw user browser:", user_agent) #Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36

    user_ip = request.remote_addr
    agent = httpagentparser.detect(user_agent)

    print("Remote IP: {} - JSON user browser {}".format(user_ip, agent))
    #Remote IP: 127.0.0.1 - JSON user browser {'platform': {'name': 'Mac OS', 'version': 'X 10.15.7'}, 'os': {'name': 'Macintosh'}, 'bot': False, 'flavor': {'name': 'MacOS', 'version': 'X 10.15.7'}, 'browser': {'name': 'Chrome', 'version': '131.0.0.0'}}

    #store user context (visitor)

    public_ip = get_public_ip()
    country,city = get_country_and_city2(public_ip)
    #print("LOCATION:", country,city)
    current_time = datetime.now()
    current_date = current_time.date()
    time_of_day = current_time.strftime("%H:%M:%S")

    session['browser'] = agent['browser'] #['name']
    session['os'] = agent['os']['name']
    session['user_ip'] = public_ip
    session['country'] = country
    session['city'] = city
    session['time_of_day'] = time_of_day
    session['current_date'] = current_date

    print(session)

    return render_template('index.html', page_title="Welcome")



@app.route('/search', methods=['POST'])
def search_form_post():
    
    search_query = request.form['search-query']

    session['last_search_query'] = search_query

    search_id = analytics_data.save_query_terms(search_query)

    #results = search_engine.search(search_query, search_id, corpus,idf,tf,index_dic,tweet_popularity,map_docid_tweetid)
    results = search_engine.search(search_query, search_id, corpus)

    print("Desde busqueda el sear_id es : ",search_id)
    found_count = len(results)
    session['last_found_count'] = found_count

    print(session)

    return render_template('results.html', results_list=results, page_title="Results", found_counter=found_count)
   

@app.route('/doc_details', methods=['GET'])
def doc_details():
    # getting request parameters:
    # user = request.args.get('user')

    print("doc details session: ")
    print(session)

    res = session["some_var"]

    print("recovered var from session:", res)

    # get the query string parameters from request
    clicked_doc_id = request.args["id"]
    p1 = int(request.args["search_id"])  # transform to Integer
    p2 = int(request.args["param2"])  # transform to Integer
    print("click in id={}".format(clicked_doc_id))

    # store data in statistics table 1
    if clicked_doc_id in analytics_data.fact_clicks.keys():
        analytics_data.fact_clicks[clicked_doc_id] += 1
    else:
        analytics_data.fact_clicks[clicked_doc_id] = 1

    print("fact_clicks count for id={} is {}".format(clicked_doc_id, analytics_data.fact_clicks[clicked_doc_id]))

    #maped_tweet_id = map_docid_tweetid[clicked_doc_id]
    doc = corpus[clicked_doc_id]

    session['search_id'] = p1
    session['param2'] = p2

    return render_template('doc_details.html', doc= doc)


@app.route('/stats', methods=['GET'])
def stats():
    """
    Show simple statistics example. ### Replace with dashboard ###
    :return:
    """

    docs = []

    # ### Start replace with your code ###
    print('In stats section')

    for doc_id in analytics_data.fact_clicks:
        row: Document = corpus[doc_id]
        count = analytics_data.fact_clicks[doc_id]
        doc = StatsDocument(row.id, row.title, row.description, row.doc_date, row.url, count)

        docs.append(doc)

    # simulate sort by ranking
    docs.sort(key=lambda doc: doc.count, reverse=True)

    return render_template('stats.html', clicks_data=docs)
    # ### End replace with your code ###


@app.route('/dashboard', methods=['GET'])
def dashboard():
    visited_docs = []
    print(analytics_data.fact_clicks.keys())
    for doc_id in analytics_data.fact_clicks.keys():
        d: Document = corpus[doc_id]
        doc = ClickedDoc(doc_id, d.description, analytics_data.fact_clicks[doc_id])
        visited_docs.append(doc.to_dict())

    # simulate sort by ranking
    visited_docs.sort(key=lambda doc: doc['counter'], reverse=True)

    #for doc in visited_docs: print(doc)


    return render_template('dashboard.html', visited_docs=visited_docs)


@app.route('/sentiment')
def sentiment_form():
    return render_template('sentiment.html')


@app.route('/sentiment', methods=['POST'])
def sentiment_form_post():
    text = request.form['text']
    nltk.download('vader_lexicon')
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    sid = SentimentIntensityAnalyzer()
    score = ((sid.polarity_scores(str(text)))['compound'])
    return render_template('sentiment.html', score=score)


if __name__ == "__main__":
    app.run(port=8088, host="0.0.0.0", threaded=False, debug=True)
