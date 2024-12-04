import json
import random
from datetime import datetime, timezone
import requests
import csv

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

        # New attributes for HTTP analytics
        self.http_requests = dict([])  # Tracks HTTP request data: key = request ID | value = request details
    
    def export_to_csv(self, filename="analytics_data.csv"):
        """
        Exports analytics data to a CSV file.
        :param filename: Name of the file to save the CSV.
        """
        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Write header
                writer.writerow(["Type", "Key", "Value"])
                
                # Write fact_clicks
                for key, value in self.fact_clicks.items():
                    writer.writerow(["fact_clicks", key, value])
                
                # Write fact_session
                for key, value in self.fact_session.items():
                    writer.writerow(["fact_session", key, value])
                
                # Write fact_request
                for key, value in self.fact_request.items():
                    writer.writerow(["fact_request", key, value])
                
                # Write search_id_to_query
                for key, value in self.search_id_to_query.items():
                    writer.writerow(["search_id_to_query", key, value])
                
                # Write dwell_times
                for key, value in self.dwell_times.items():
                    writer.writerow(["dwell_times", key, value])
                
                # Write fact_sessions
                for session_id, session_user in self.fact_sessions.items():
                    writer.writerow(["fact_sessions", session_id, json.dumps(session_user.to_dict())])

                # Write doc_to_queries
                for key, value in self.doc_to_queries.items():
                    writer.writerow(["doc_to_queries", key, value])
                
                # Write http_requests
                for key, value in self.http_requests.items():
                    writer.writerow(["http_requests", key, value])
            
            print(f"Analytics data successfully exported to {filename}.")
        except Exception as e:
            print(f"An error occurred while exporting data: {e}")

    def log_http_request(self, endpoint, method, status_code, ip_address, timestamp):
        """Log HTTP request details."""
        request_id = random.randint(0, 100000)
        self.http_requests[request_id] = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "ip_address": ip_address,
            "timestamp": timestamp
        }
        return request_id

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
