import json
import random
from datetime import datetime, timezone
import requests

class AnalyticsData:
    """
    An in memory persistence object.
    Declare more variables to hold analytics tables.
    """
    def __init__(self):
        self.fact_clicks = dict([]) # statistics table 1 - dictionary with the click counters: key = doc id | value = click counter
        self.fact_session = dict([]) # statistics table 2
        self.fact_request = dict([]) # statistics table 3
        self.search_id_to_query = dict([]) # util dictionary to map query terms to request id
        self.dwell_times = dict([]) 
        self.fact_sessions = dict([])
        self.doc_to_queries = dict([])
        
    def query_terms_to_request_id(self, terms: str) -> int: # same query terms has same request id
        if terms in self.search_id_to_query.keys():
            return self.search_id_to_query[terms] # return the request id
        else:
            return random.randint(0, 100000)

    def save_query_terms(self, terms: str) -> int:
        # fact_request should be a dict with key = query terms and value = times requested
        if terms in self.fact_request.keys():
            self.fact_request[terms] += 1
        else:
            self.fact_request[terms] = 1

        # return a request id for the query term saved
        request_id = self.query_terms_to_request_id(terms)
        return request_id   

class ClickedDoc:
    def __init__(self, doc_id, description, counter):
        self.doc_id = doc_id
        self.description = description
        self.counter = counter

    def to_json(self):

        return self.__dict__

    def to_dict(self):
        return {
            "doc_id" : self.doc_id,
            "description" : self.description,
            "counter" : self.counter
        }

        
        
    def __str__(self):
        """
        Print the object content as a JSON string
        """
        return json.dumps(self)


class SessionUser:
    def __init__(self):
        self.browser = None
        self.os = None
        self.user_ip = None
        self.country = None
        self.city = None
        self.last_search_query = None
        self.last_search_id = None
        self.last_found_count = None
        self.dwell_time = None
        self.clicked_doc_id = None
        self.click_time = None
        self.current_date = None
        self.time_of_day = None

    @staticmethod
    def get_public_ip():
        try:
            response = requests.get('https://api64.ipify.org?format=json')
            return response.json()['ip']
        except Exception as e:
            print(f"Error fetching public IP: {e}")
            return "Unknown"

    @staticmethod
    def get_country_and_city(ip_address):
        try:
            response = requests.get(f'https://ipinfo.io/{ip_address}/json')
            data = response.json()
            country = data.get('country', 'Unknown')
            city = data.get('city', 'Unknown')
            return country, city
        except Exception as e:
            print(f"Error fetching country and city: {e}")
            return "Unknown", "Unknown"


    def update_browser_data(self, browser, os, user_ip, country, city,  current_date, time_of_day):
        self.browser = browser
        self.os = os
        self.user_ip = user_ip
        self.country = country
        self.city = city
        self.current_date = current_date
        self.time_of_day = time_of_day

    def update_search_data(self, search_query, search_id, found_count):
        self.last_search_query = search_query
        self.last_search_id = search_id
        self.last_found_count = found_count

    def update_dwell_time(self, click_time):
        click_time_naive = click_time.replace(tzinfo=None)
        self.dwell_time = (datetime.now() - click_time_naive).total_seconds()

    def update_clicked_doc(self, doc_id, click_time):
        self.clicked_doc_id = doc_id
        self.click_time = click_time

    def to_dict(self):
        return {
            'browser': self.browser,
            'os': self.os,
            'user_ip': self.user_ip,
            'country': self.country,
            'city': self.city,
            'last_search_query': self.last_search_query,
            'last_search_id': self.last_search_id,
            'last_found_count': self.last_found_count,
            'dwell_time': self.dwell_time,
            'clicked_doc_id': self.clicked_doc_id,
            'click_time': self.click_time,
            'current_date': self.current_date,
            'time_of_day': self.time_of_day
        }
