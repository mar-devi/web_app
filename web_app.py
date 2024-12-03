import os
from json import JSONEncoder
import uuid
import httpagentparser 
import nltk
from flask import Flask, render_template, session, request, redirect, url_for
import requests
from datetime import datetime, timezone

from myapp.analytics.analytics_data import AnalyticsData, ClickedDoc, SessionUser
from myapp.search.load_corpus import load_corpus
from myapp.search.objects import Document, StatsDocument
from myapp.search.search_engine import SearchEngine
from myapp.core.utils import load_csv_file


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

    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4()) 
    session_id = session['session_id']
    print(f"Session ID: {session_id}")

    user_agent = request.headers.get('User-Agent')
    print("Raw user browser:", user_agent) 
    user_ip = request.remote_addr
    agent = httpagentparser.detect(user_agent)

    print("Remote IP: {} - JSON user browser {}".format(user_ip, agent))

    #store user context (visitor)
    public_ip = get_public_ip()
    country,city = get_country_city(public_ip)
    current_time = datetime.now()
    current_date = current_time.date()
    time_of_day = current_time.strftime("%H:%M:%S")

    browser = agent.get('browser', {}).get('name', 'Unknown')
    os = agent.get('os', {}).get('name', 'Unknown')

    session_user = SessionUser()
    session_user.update_browser_data(browser, os, public_ip, country, city, str(current_date), time_of_day)

    # Guardar la información de la sesión en `fact_sessions`
    analytics_data.fact_sessions[session_id] = session_user

    session['browser'] = agent['browser'] #['name']
    session['os'] = agent['os']['name']
    session['user_ip'] = public_ip
    session['country'] = country
    session['city'] = city
    session['time_of_day'] = time_of_day
    session['current_date'] = current_date


    return render_template('index.html', page_title="Welcome")



@app.route('/search', methods=['POST'])
def search_form_post():
    
    search_query = request.form['search-query']

    session['last_search_query'] = search_query

    search_id = analytics_data.save_query_terms(search_query)
    session['last_search_id'] = search_id
    
    session_user_data = session.get('user', {})
    session_user = SessionUser()
    session_user.__dict__.update(session_user_data)

    results = search_engine.search(search_query, search_id, corpus)

    session_user.update_search_data(search_query, search_id, len(results))
    session['user'] = session_user.to_dict()

    print("Desde busqueda el sear_id es : ",search_id)
    found_count = len(results)
    session['last_found_count'] = found_count

    print(session)

    return render_template('results.html', results_list=results, page_title="Results", found_counter=found_count)


@app.route('/search', methods=['GET'])
def search_not_post():
    
    #print(f"click time now : {session['click_time']}")
    
    click_time_aware = session['click_time']
    click_time_naive = click_time_aware.replace(tzinfo=None)
    session['dwell_time'] =  (datetime.now() - click_time_naive).total_seconds()
    print(f"Dwell time difference: {session['dwell_time']}")

    # handle dwell time for the clicked document
    if session['clicked_doc_id'] not in analytics_data.dwell_times:
            analytics_data.dwell_times[session['clicked_doc_id']] = []

    analytics_data.dwell_times[session['clicked_doc_id']].append(session['dwell_time'])
    
    search_query = session["last_search_query"]
    search_id = session['last_search_id']
    print(search_query,search_id)
    results = search_engine.search(search_query, search_id, corpus)

    found_count = len(results)

    # for each doc in the results
    # if the doc is clicked -> add its related search query (for stats)
    for doc in results:
        if doc.id == session['clicked_doc_id']:
            if doc.id not in analytics_data.doc_to_queries:
                analytics_data.doc_to_queries[doc.id] = []
                analytics_data.doc_to_queries[doc.id].append(search_query)
            else:
                if search_query not in analytics_data.doc_to_queries[doc.id]:
                    analytics_data.doc_to_queries[doc.id].append(search_query)
    
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

    session['clicked_doc_id'] = clicked_doc_id


    session['click_time'] = datetime.now()

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
        all_times_docid = analytics_data.dwell_times[doc_id]
        queries = analytics_data.doc_to_queries[doc_id]

        if len(all_times_docid) == 0: # handle division by zero
            avg_dwell_time = 0
        else:
            avg_dwell_time = sum(all_times_docid) / len(all_times_docid) 

        doc = StatsDocument(row.id, row.title, row.description, row.doc_date, row.url, count, avg_dwell_time, queries)
        
        docs.append(doc)

    # simulate sort by ranking
    docs.sort(key=lambda doc: doc.count, reverse=True)

    return render_template('stats.html', clicks_data=docs)


@app.route('/dashboard', methods=['GET'])
def dashboard():

    visitor_stats = len(analytics_data.fact_sessions)
    session_stats = sum(1 for session_user in analytics_data.fact_sessions.values() if session_user)
    total_searches = sum(analytics_data.fact_request.values())
    
    browser_distribution = {}
    os_distribution = {}
    country_distribution = {}
    city_distribution = {}
    time_of_day_stats = {}
    date_stats = {}
    for user_session in analytics_data.fact_sessions.values():
        browser = user_session.browser
        if browser in browser_distribution:
            browser_distribution[browser] += 1
        else:
            browser_distribution[browser] = 1
        
        os = user_session.os
        os_distribution[os] = os_distribution.get(os, 0) + 1

        # Country distribution
        country = user_session.country
        country_distribution[country] = country_distribution.get(country, 0) + 1

        # City distribution
        city = user_session.city
        city_distribution[city] = city_distribution.get(city, 0) + 1

        # Time of day stats
        time_of_day = user_session.to_dict().get('time_of_day', 'Unknown')
        if time_of_day != 'Unknown':
            hour = int(time_of_day.split(':')[0])  # Extract the hour
            grouped_hour = f"{hour:02d}:00-{hour:02d}:59"  # Create the interval
            time_of_day_stats[grouped_hour] = time_of_day_stats.get(grouped_hour, 0) + 1
        # time_of_day_stats[time_of_day] = time_of_day_stats.get(time_of_day, 0) + 1

        # Date stats
        current_date = user_session.to_dict().get('current_date', 'Unknown')
        date_stats[current_date] = date_stats.get(current_date, 0) + 1

    browser_distribution = dict(sorted(browser_distribution.items(), key=lambda x: x[1], reverse=True))
    os_distribution = dict(sorted(os_distribution.items(), key=lambda x: x[1], reverse=True))
    country_distribution = dict(sorted(country_distribution.items(), key=lambda x: x[1], reverse=True))
    city_distribution = dict(sorted(city_distribution.items(), key=lambda x: x[1], reverse=True))

    print("Browser distribution:", browser_distribution)

    # visited_docs = []
    # print(analytics_data.fact_clicks.keys())
    # for doc_id in analytics_data.fact_clicks.keys():
    #     d: Document = corpus[doc_id]
    #     doc = ClickedDoc(doc_id, d.description, analytics_data.fact_clicks[doc_id])
    #     visited_docs.append(doc.to_dict())
    visited_docs = [
        ClickedDoc(doc_id, corpus[doc_id].description, analytics_data.fact_clicks[doc_id]).to_dict()
        for doc_id in analytics_data.fact_clicks.keys()
    ]
    visited_docs.sort(key=lambda doc: doc['counter'], reverse=True)

    query_stats = len(analytics_data.fact_request) # number of unique queries
    queries_made = analytics_data.fact_request # unique queries

    unique_queries = []
    for query in queries_made.keys():
        unique_queries.append({"query": query, "count": queries_made[query]})

    return render_template('dashboard.html', 
                           browser_distribution=browser_distribution,
                           total_searches=total_searches,
                           visitor_stats=visitor_stats,
                           session_stats=session_stats,
                           visited_docs=visited_docs, 
                           query_stats=query_stats, 
                           unique_queries=unique_queries,
                           os_distribution=os_distribution,
                           country_distribution=country_distribution,
                           city_distribution=city_distribution,
                           time_of_day_stats=time_of_day_stats,
                           date_stats=date_stats,)


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
