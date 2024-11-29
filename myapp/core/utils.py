import datetime
import json
from random import random
import pickle
from faker import Faker
import pandas as pd
fake = Faker()
import os


# fake.date_between(start_date='today', end_date='+30d')
# fake.date_time_between(start_date='-30d', end_date='now')
#
# # Or if you need a more specific date boundaries, provide the start
# # and end dates explicitly.
# start_date = datetime.date(year=2015, month=1, day=1)
# fake.date_between(start_date=start_date, end_date='+30y')

def get_random_date():
    """Generate a random datetime between `start` and `end`"""
    return fake.date_time_between(start_date='-30d', end_date='now')


def get_random_date_in(start, end):
    """Generate a random datetime between `start` and `end`"""
    return start + datetime.timedelta(
        # Get a random amount of seconds between `start` and `end`
        seconds=random.randint(0, int((end - start).total_seconds())), )

def load_csv_file(archivo):
    '''
    Load a csv file from the given path and returns a dataframe
    
    Parameters:
    path (string): the file path

    Returns:
    dataframe object

    '''
    full_path = os.path.realpath(__file__)
    path, filename = os.path.split(full_path)
    file_path = os.path.join(path, "../../data/")
    file_path = os.path.join(file_path, archivo)
    file_path = os.path.normpath(file_path)
    data = pd.read_csv(file_path)
    data_dict = document_id_map = dict(zip(data['id'],data['docId']))

    return data_dict



def load_pkl_file(archivo):
    """
    Load a pickle file from the given path and return the deserialized object.

    Parameters:
    path (string): The path to the .pkl file.

    Returns:
    object: The deserialized object stored in the pickle file.
    """
    full_path = os.path.realpath(__file__)
    path, filename = os.path.split(full_path)
    file_path = os.path.join(path, "../../data/")
    file_path = os.path.join(file_path, archivo)
    file_path = os.path.normpath(file_path)

    with open(file_path, 'rb') as file:
        data = pickle.load(file)
    return data    

def load_json_file(archivo):
    """Load JSON content from file in 'path'

    Parameters:
    path (string): the file path

    Returns:
    JSON: a JSON object
    """

    # Load the file into a unique string
    #with open(path) as fp:
     #   text_data = fp.readlines()
    
    #with open(path, 'r') as fp:
        # Leer todas las líneas y convertir cada línea en un objeto JSON
        #json_data = [json.loads(line.strip()) for line in fp]
    

    json_data = pd.read_json(archivo, lines=True)
  
    # Parse the string into a JSON object
    #json_data = json.loads(text_data)

    #json is a dictionary
  
    
    return json_data
