import pandas as pd

from myapp.core.utils import load_json_file, load_tweet_id_mapping
from myapp.search.objects import Document
from myapp.core.utils import  load_csv_file
from typing import List

_corpus = {}

# path_data = '/Users/uni/Documents/4upf/1trim/IR/final part/search-engine-web-app-main' + '/data'
# map_tweetid_docid = load_csv_file(path_data + '/tweet_document_ids_map.csv')

map_tweetid_docid = load_tweet_id_mapping()

def load_corpus(path) -> List[Document]:
    """
    Load file and transform to dictionary with each document as an object for easier treatment when needed for displaying
     in results, stats, etc.
    :param path:
    :return:
    """
    #df = _load_corpus_as_dataframe(path)
    df = _load_corpus_as_dataframe_farmer(path)
    df.apply(_row_to_doc_dict, axis=1)
    return _corpus


def _load_corpus_as_dataframe(path):
    """
    Load documents corpus from file in 'path'
    :return:
    """
    json_data = load_json_file(path)
    tweets_df = _load_tweets_as_dataframe(json_data.items())
    _clean_hashtags_and_urls(tweets_df)
    # Rename columns to obtain: Tweet | Username | Date | Hashtags | Likes | Retweets | Url | Language
    corpus = tweets_df.rename(
        columns={"id": "Id", "full_text": "Tweet", "screen_name": "Username", "created_at": "Date",
                 "favorite_count": "Likes",
                 "retweet_count": "Retweets", "lang": "Language"})

    # select only interesting columns
    filter_columns = ["Id", "Tweet", "Username", "Date", "Hashtags", "Likes", "Retweets", "Url", "Language"]
    corpus = corpus[filter_columns]
    return corpus

def  _load_corpus_as_dataframe_farmer(path):
    """
    Load documents corpus from file in 'path'
    :return: dict
    """
    json_data = load_json_file(path)

    #tweets_df = pd.DataFrame([json_data]) 
    tweets_df = pd.DataFrame(json_data)
    tweets_df = tweets_df[tweets_df['lang'] == 'en'].reset_index(drop=True)
    #Nested columns like 'Username'
    username_column = tweets_df['user'].apply(pd.Series)['username']

    tweets_df = pd.concat([tweets_df, username_column.rename('username')], axis=1)

    # Rename columns to obtain: Tweet | Username | Date | Hashtags | Likes | Retweets | Url | Language
    corpus = tweets_df.rename(
        columns={'id': 'Id','content': 'Tweet','username': 'Username','date': 'Date', 'likeCount': 'Likes', 'retweetCount': 'Retweets', 'url': 'Url', 'lang': 'Language'})

   #Create column Hashtags 
    corpus['Hashtags'] = corpus['Tweet'].apply(lambda x: [i for i in x.split() if i.startswith("#")]) 
    
    # select only interesting columns
    filter_columns = ["Id", "Tweet", "Username", "Date", "Hashtags", "Likes", "Retweets", "Url", "Language"]
    corpus = corpus[filter_columns]

    #username ?

    corpus['Date'] = pd.to_datetime(corpus['Date'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')

    #print(corpus.head())
    return corpus



def _load_tweets_as_dataframe(json_data):
    '''Converts dictionary data into a pandas DataFrame and processes specific nested structures, like hashtags and user data, into individual columns.'''
    data = pd.DataFrame(json_data).transpose()

    # parse entities as new columns
    data = pd.concat([data.drop(['entities'], axis=1), data['entities'].apply(pd.Series)], axis=1)
    # parse user data as new columns and rename some columns to prevent duplicate column names
    data = pd.concat([data.drop(['user'], axis=1), data['user'].apply(pd.Series).rename(
        columns={"created_at": "user_created_at", "id": "user_id", "id_str": "user_id_str", "lang": "user_lang"})],
                     axis=1)
    return data


def _build_tags(row):
    tags = []
    # for ht in row["hashtags"]:
    #     tags.append(ht["text"])
    for ht in row:
        tags.append(ht["text"])
    return tags


def _build_url(row):
    url = ""
    try:
        url = row["entities"]["url"]["urls"][0]["url"]  # tweet URL
    except:
        try:
            url = row["retweeted_status"]["extended_tweet"]["entities"]["media"][0]["url"]  # Retweeted
        except:
            url = ""
    return url


def _clean_hashtags_and_urls(df):
    df["Hashtags"] = df["hashtags"].apply(_build_tags)
    df["Url"] = df.apply(lambda row: _build_url(row), axis=1)
    # df["Url"] = "TODO: get url from json"
    df.drop(columns=["entities"], axis=1, inplace=True)


def load_tweets_as_dataframe2(json_data):
    """Load json into a dataframe

    Parameters:
    path (string): the file path

    Returns:
    DataFrame: a Panda DataFrame containing the tweet content in columns
    """
    # Load the JSON as a Dictionary
    tweets_dictionary = json_data.items()
    # Load the Dictionary into a DataFrame.
    dataframe = pd.DataFrame(tweets_dictionary)
    # remove first column that just has indices as strings: '0', '1', etc.
    dataframe.drop(dataframe.columns[0], axis=1, inplace=True)
    return dataframe


def load_tweets_as_dataframe3(json_data):
    """Load json data into a dataframe

    Parameters:
    json_data (string): the json object

    Returns:
    DataFrame: a Panda DataFrame containing the tweet content in columns
    """

    # Load the JSON object into a DataFrame.
    dataframe = pd.DataFrame(json_data).transpose()

    # select only interesting columns
    filter_columns = ["id", "full_text", "created_at", "entities", "retweet_count", "favorite_count", "lang"]
    dataframe = dataframe[filter_columns]
    return dataframe


def _row_to_doc_dict(row: pd.Series):
    #print(map_tweetid_docid[row["Id"]])
    doc_id = map_tweetid_docid[row['Id']]
    _corpus[doc_id] = Document(doc_id, row['Tweet'][0:100], row['Tweet'], row['Date'], row['Likes'],
                                  row['Retweets'],
                                  row['Url'], row['Hashtags'])
    #print(_corpus[doc_id])