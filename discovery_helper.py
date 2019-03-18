import json
import os
from os import listdir
from os.path import isfile, join
from pathlib import Path, PureWindowsPath
from watson_developer_cloud import DiscoveryV1
from urllib.request import pathname2url
from get_htm import find as find_htm_files


BASE_URL_ONLINE = 'http://help.central.arubanetworks.com/latest/documentation/online_help/'
BASE_URL_OFFLINE = 'C:/Users/manikvig/Desktop/'
ENV_ID = "7206305c-d647-41f2-a1cc-eb909ec2c641"

discovery = DiscoveryV1(
    version="2018-12-03",
    url = "https://gateway-wdc.watsonplatform.net/discovery/api",
    iam_apikey='gTAsSzZBIxtS_p5g1-JBIjfeXs0F2a0DtOZI7YAzO2Hk'
)

# For Creating a new Collection
def createCollection(env_id, name, desc, lang):
    """
    params: Environment ID, Collection Name, Collection Description, Collection Language
    returns: details of the newly created collection as JSON
    """
    new_collection = discovery.create_collection(environment_id=env_id, configuration_id='', name=name, description=desc, language=lang).get_result()
    print(json.dumps(new_collection, indent=2))
    return new_collection

# For Listing all collections in the Environment
def listCollections(env_id):
    """
    params: requires Environment ID
    returns: list of all collections in JSON
    """
    collections = discovery.list_collections(ENV_ID).get_result()
    print(json.dumps(collections, indent=2))
    return collections

# For getting details of a particular collection
def collectionDetails(env_id, collection_id):
    """
    params: Environment ID and Collection ID
    returns: details of the given collection as JSON
    """
    collection = discovery.get_collection(ENV_ID, COLLECTION_ID).get_result()
    print(json.dumps(collection, indent=2))
    return collection

# For Updating exisiting collection
def updateCollection(env_id, collection_id, config_id, name, desc):
    """
    params: Environment ID, Collection ID, Collection Name, Collection Description
    returns: updated collection details in JSON
    """
    updated_collection = discovery.update_collection(environment_id=env_id, collection_id=collection_id, configuration_id=config_id, name=name, description=desc).get_result()
    print(json.dumps(updated_collection, indent=2))
    return updated_collection

# For Deleting collection
def deleteCollection(env_id, collection_id):
    """
    params: Environment ID, Collection ID
    returns: status of delete operation (on collection) as JSON
    """
    delete_collection = discovery.delete_collection(env_id, collection_id).get_result()
    print(json.dumps(delete_collection, indent=2))
    return delete_collection

# For Uploading HTM files to Discovery
def uploadDocumentsToDiscovery(url, regex, url_base):
    """
    params: 
        url - local path (file path or directory path)
        regex - regular expression to match particular extension
        url_base - path to be added as meta to each document
    returns: prints the details of the uploaded documents
    """
    htm_files_list = find_htm_files(url , regex)
    print("Number of HTM files found: ", len(htm_files_list))
    
    for x in htm_files_list:
        meta = url_base + str(pathname2url(x))
        meta_dict = {"source_url": meta}
        to_open = os.path.join(Path(BASE_URL_OFFLINE), x)
        with open(to_open, encoding='UTF-8') as f:
            add_doc = discovery.add_document(ENV_ID, COLLECTION_ID, file=f, metadata=json.dumps(meta_dict), filename=meta).get_result()

    print(json.dumps(add_doc, indent=2))
    return add_doc

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

if __name__ == '__main__':
    # ------------------------ #
    # New Collection           #
    # ------------------------ #
    new_collection = createCollection(ENV_ID, 'AI Search', 'Collection for Aruba Central\'s AI Search', 'en')
    print(json.dumps(new_collection, indent=2))

    # ------------------------ #
    # List Collection          #
    # ------------------------ #
    collections = listCollections(ENV_ID)
    COLLECTION_ID = collections.get("collections")[0].get("collection_id")

    # ------------------------ #
    # Get Collection Details   #
    # ------------------------ #
    collection = collectionDetails(ENV_ID, COLLECTION_ID)
    CONFIG_ID = collection.get("configuration_id")

    # ------------------------ #
    # Upload Documents         #
    # ------------------------ #
    regex = "\w*\.htm"
    added_document = uploadDocumentsToDiscovery(BASE_URL_OFFLINE, regex, BASE_URL_ONLINE)
    print(json.dumps(added_document, indent=2))

    # ------------------------ #
    # Stopword Status          #
    # ------------------------ #
    print(json.dumps(getStopWordStatus(ENV_ID, COLLECTION_ID), indent=2))

    # ------------------------ #
    # Upload Stopword list     #
    # ------------------------ #
    sw_file_path = Path('C:/Users/manikvig/Documents/Work/discovery-file-upload/aruba_search_stopwords.txt')
    with open(sw_file_path, encoding='UTF-8') as sw_file:
        print(json.dumps(addStopWords(ENV_ID, COLLECTION_ID, sw_file, 'Aruba Search Stopwords')))