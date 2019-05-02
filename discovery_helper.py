import json
import os
import codecs
from os import listdir
from os.path import isfile, join
from glob import glob
from pathlib import Path, PureWindowsPath
from watson_developer_cloud import DiscoveryV1
from urllib.request import pathname2url
from get_htm import find as find_htm_files


BASE_URL_ONLINE = '<SERVER_BASE_PATH>'
BASE_URL_OFFLINE = '<LOCAL_BASE_PATH>'
ENV_ID = '<ENVIRONMENT_ID>'

discovery = DiscoveryV1(
    version="<VERSION>",
    url="https://gateway-wdc.watsonplatform.net/discovery/api",
    iam_apikey='<YOUR_API_KEY>'
)

# For Creating a new Collection


def createCollection(env_id, name, desc, lang):
    """
    params: Environment ID, Collection Name, Collection Description, Collection Language
    returns: details of the newly created collection as JSON
    """
    new_collection = discovery.create_collection(
        environment_id=env_id, configuration_id='', name=name, description=desc, language=lang).get_result()
    print(json.dumps(new_collection, indent=2))
    return new_collection

# For Listing all collections in the Environment


def listCollections(env_id):
    """
    params: requires Environment ID
    returns: list of all collections in JSON
    """
    collections = discovery.list_collections(env_id).get_result()
    print(json.dumps(collections, indent=2))
    return collections

# For getting details of a particular collection


def collectionDetails(env_id, collection_id):
    """
    params: Environment ID and Collection ID
    returns: details of the given collection as JSON
    """
    collection = discovery.get_collection(env_id, collection_id).get_result()
    print(json.dumps(collection, indent=2))
    return collection

# For Updating exisiting collection


def updateCollection(env_id, collection_id, config_id, name, desc):
    """
    params: Environment ID, Collection ID, Collection Name, Collection Description
    returns: updated collection details in JSON
    """
    updated_collection = discovery.update_collection(
        environment_id=env_id, collection_id=collection_id, configuration_id=config_id, name=name, description=desc).get_result()
    print(json.dumps(updated_collection, indent=2))
    return updated_collection

# For Deleting collection


def deleteCollection(env_id, collection_id):
    """
    params: Environment ID, Collection ID
    returns: status of delete operation (on collection) as JSON
    """
    delete_collection = discovery.delete_collection(
        env_id, collection_id).get_result()
    print(json.dumps(delete_collection, indent=2))
    return delete_collection

# For Uploading HTM files to Discovery


def globDocumentsToDiscovery(url, regex, url_base, env_id, collection_id):
    """
    DOCUMENT GLOBBER
    params: 
        url - local path (file path or directory path)
        regex - regular expression to match particular extension
        url_base - path to be added as meta to each document
    returns: prints the details of the uploaded documents
    """
    htm_files_list = find_htm_files(url, regex)
    print('{} files in ../content folder\n'.format(len(htm_files_list)))
    ftu_list = []

    for content_htm in htm_files_list:
        meta = url_base + str(pathname2url(content_htm))
        meta_dict = {"source_url": meta}

        # passing each HTML file in content folder to globber to find match
        parsed_htm_list = glob('<PATH>')
        print('{} files in ../parsed_htm folder\n'.format(len(parsed_htm_list)))
        content_file_name = (content_htm.split('\\')[-1]).split('.')[0]

        for parsed_htm in parsed_htm_list:
            parsed_file_name = (parsed_htm.split('\\')[-1]).split('.')[0]
            if parsed_file_name == content_file_name:
                with open(Path(parsed_htm), encoding='UTF-8') as f:
                    add_doc = discovery.add_document(
                        env_id, collection_id, file=f, metadata=json.dumps(meta_dict), filename=meta).get_result()
                    print(add_doc)
            else:
                pass


def uploadDocumentsToDiscovery(url, regex, url_base, env_id, collection_id):
    """
    DIRECT UPLOAD
    params: 
        url - local path (file path or directory path)
        regex - regular expression to match particular extension
        url_base - path to be added as meta to each document
    returns: prints the details of the uploaded documents
    """
    htm_files_list = find_htm_files(url, regex)
    print('{} files in ../content folder\n'.format(len(htm_files_list)))

    for htm in htm_files_list:
        to_open = os.path.join(Path(BASE_URL_OFFLINE), htm)
        meta = url_base + str(pathname2url(htm))
        meta_dict = {"source_url": meta}
        with open(Path(to_open), encoding='UTF-8') as f:
            add_doc = discovery.add_document(env_id, collection_id,
                                             file=f, metadata=json.dumps(meta_dict), filename=meta).get_result()
            print(json.dumps(add_doc, indent=4))


def getStopWordStatus(env_id, collection_id):
    """
    params: Environment ID and Collection ID
    returns: Details of available stopword list in JSON
    """
    try:
        result = discovery.get_stopword_list_status(env_id, collection_id)
        return result
    except:
        return '{\'Exception\': Watson API Exception}'


def addStopWords(env_id, collection_id, sw_file, sw_file_name):
    """
    params: Environment ID, Collection ID, Stopword File, Stopword File name (optional, 'None' by default)
    returns: Details of the ingested stopword file as JSON
    """
    return discovery.create_stopword_list(env_id, collection_id, sw_file, sw_file_name)


def queryDiscovery(env_id, collection_id, query):
    """
    params: query string
    returns: query response as JSON
    """
    return discovery.query(
        environment_id=env_id,
        collection_id=collection_id,
        natural_language_query=query,
        count=1,
        passages=True,
        return_fields="text",
        passage_count=3,
        passage_characters=1000
    )
