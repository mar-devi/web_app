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


def load_tweet_id_mapping():
    full_path = os.path.realpath(__file__)
    path, filename = os.path.split(full_path)
    file_path = os.path.join(path, "../../data/tweet_document_ids_map.csv")
    file_path = os.path.normpath(file_path)
    
    # Read the file once
    tweet_document_ids_map = pd.read_csv(file_path)
    
    # Convert it to a dictionary for faster lookups
    return dict(zip(tweet_document_ids_map["id"], tweet_document_ids_map["docId"]))


import csv
import csv
import ast

def load_analytics_info_dwell(file_path):
    """
    Carga un archivo CSV con columnas 'Key' y 'Value' donde 'Value' es una cadena que representa una lista de números.

    Args:
        file_path (str): Ruta al archivo CSV.

    Returns:
        dict: Diccionario donde las claves son 'Key' y los valores son listas de números.
    """
    analytics_dict = {}

    try:
        # Abrir el archivo CSV
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            
            # Leer la primera fila como encabezado
            header = next(reader)
            if header != ['Key', 'Value']:
                raise ValueError("El archivo CSV debe tener columnas 'Key' y 'Value'.")
            
            # Leer las filas y construir el diccionario
            for row in reader:
                key = row[0]
                value = row[1]

                # Convertir el valor de texto que representa una lista a una lista real
                try:
                    value_list = ast.literal_eval(value)  # Convierte la cadena a una lista
                    if isinstance(value_list, list):  # Verificar que sea una lista
                        analytics_dict[key] = value_list
                    else:
                        raise ValueError(f"El valor para {key} no es una lista válida.")
                except (ValueError, SyntaxError) as e:
                    print(f"Error al procesar el valor para {key}: {e}")

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en la ruta '{file_path}'.")
    except Exception as e:
        print(f"Ha ocurrido un error inesperado: {e}")

    return analytics_dict

def load_analytics_info(file_path):
    """
    Carga un archivo CSV con columnas 'Key' y 'Value' en un diccionario.

    Args:
        file_path (str): Ruta al archivo CSV.

    Returns:
        dict: Diccionario con los datos del CSV (clave = Key, valor = Value).
    """
    analytics_dict = {}

    try:
        # Abrir el archivo CSV
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            
            # Leer la primera fila como encabezado
            header = next(reader)
            if header != ['Key', 'Value']:
                raise ValueError("El archivo CSV debe tener columnas 'Key' y 'Value'.")
            
            # Leer las filas y construir el diccionario
            for row in reader:
                key = row[0]
                value = int(row[1])  # Convertir el valor a entero
                analytics_dict[key] = value

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en la ruta '{file_path}'.")
    except ValueError as e:
        print(f"Error en el formato del archivo CSV: {e}")
    except Exception as e:
        print(f"Ha ocurrido un error inesperado: {e}")

    return analytics_dict

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
    

    json_data = pd.read_json(archivo, lines=True, compression='gzip')
  
    # Parse the string into a JSON object
    #json_data = json.loads(text_data)

    #json is a dictionary
  
    
    return json_data
