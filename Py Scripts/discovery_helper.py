import time
import json
import os
import codecs
import sys
import argparse
from os.path import join
from glob import glob
from pathlib import Path, PureWindowsPath
from watson_developer_cloud import DiscoveryV1
from urllib.request import pathname2url
from get_htm import find as find_htm_files
from excel_parser import xl_iterator as xli 
from openpyxl import  load_workbook, Workbook
import watson_training_utils as wtu
import s3_utils as s3u
import subprocess

# Start timer
start_time = time.time()
print('Executing Discovery Utils...')

# For Creating a new Collection

def createCollection(env_id, name = None, desc = None, lang = None, config = None):
    """
    params: Environment ID, Collection Name, Collection Description, Collection Language
    returns: details of the newly created collection as JSON
    """
    name = name if name else input('Please specify a name for your new collection: ')
    new_collection = discovery.create_collection(environment_id = env_id, configuration_id = config if config else '', name = name, description = desc if desc else '', language = lang if lang else '').get_result()
    print(json.dumps(new_collection, indent = 4))
    return new_collection

# For Listing all collections in the Environment

def listCollections(env_id):
    """
    params: requires Environment ID
    returns: list of all collections in JSON
    """
    collections = discovery.list_collections(env_id).get_result()
    print(json.dumps(collections, indent = 4))
    return collections

# For getting details of a particular collection

def getCollection(env_id, collection_id = None):
    """
    params: Environment ID and Collection ID
    returns: details of the given collection as JSON
    """
    collection_id = collection_id if collection_id else input('ID of collection to be listed: ')
    collection = discovery.get_collection(env_id, collection_id).get_result()
    print(json.dumps(collection, indent = 4))
    return collection

# For Updating exisiting collection

def updateCollection(env_id, collection_id = None, config_id = None, name = None, desc = None, flag = None):
    """
    params: Environment ID, Collection ID, Collection Name, Collection Description
    returns: updated collection details in JSON
    """
    name = name if name else input('Please provide a name for the collection: ')
    collection_id = collection_id if collection_id else input('ID of collection to be updated: ')
    flag = flag if flag else input('Do you want to update configuration? (Y/N): ')
    
    if flag == 'Y' or flag == 'y' or flag == 'yes' or flag == 'Yes' or flag == True:
        config_id = config_id if config_id else input('Please provide the new configuration ID: ')
    else:
        print('Ok, configuration is not changed.')
    
    updated_collection = discovery.update_collection(
        environment_id = env_id,
        collection_id = collection_id,
        configuration_id = config_id,
        name = name,
        description = desc).get_result()
    print(json.dumps(updated_collection, indent = 4))
    return updated_collection

# For Deleting collection

def deleteCollection(env_id, collection_id = None):
    """
    params: Environment ID, Collection ID
    returns: status of delete operation (on collection) as JSON
    """
    collection_id = collection_id if collection_id else input('ID of collection to be deleted: ')
    delete_collection = discovery.delete_collection(
    env_id, collection_id).get_result()
    print(json.dumps(delete_collection, indent = 4))
    return delete_collection

# For creating configuration

def createConfig(env_id, config_path = None):
    config_path = config_path if config_path else Path(input('Please provide actual path for configuration file: '))

    with open(Path(config_path)) as config_data:
        data = json.load(config_data)
        new_config = discovery.create_configuration(env_id, data['name'], data['description'], data['conversions'], data['enrichments'], data['normalizations']).get_result()
    print(json.dumps(new_config, indent = 4))
    
    return new_config

# For deleting configuration

def deleteConfig(env_id, config_id = None):
    
    config_id = config_id if config_id else input('ID of configuration to be deleted: ')
    config_delete = discovery.delete_configuration(env_id, config_id).get_result()
    print(json.dumps(config_delete, indent = 4))
    
    return config_delete

# For updating configuration

def updateConfig(env_id, config_id = None, config_path = None, config_name = None, config_desc = None):
    config_id = config_id if config_id else input('ID of configuration to be updated: ')
    config_path = config_path if config_path else Path(input('Please provide actual path for configuration file: '))

    with open(Path(config_path)) as config_data:
        data = json.load(config_data)
        data['name'] = config_name if config_name else data['name']
        data['description'] = config_desc if config_desc else data['description']
        updated_config = discovery.update_configuration(env_id, config_id, data['name'], data['description'], data['conversions'], data['enrichments'], data['normalizations']).get_result()
    print(json.dumps(updated_config, indent = 4))
    return updated_config

# For listing configurations

def listConfig(env_id):
    configs = discovery.list_configurations(env_id).get_result()
    print(json.dumps(configs, indent = 4))
    return configs

# For showing configuration details

def getConfig(env_id, config_id = None):
    config_id = config_id if config_id else input('Please input ID of configuration to be displayed: ')
    config = discovery.get_configuration(env_id, config_id).get_result()
    print(json.dumps(config, indent = 4))
    return config

# For Uploading HTM files to Discovery with glob collector

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

# For Uploading HTM files to Discovery with glob collector

def uploadLocalDocumentsToDiscovery(url, regex, url_base, env_id, collection_id):
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
        to_open = os.path.join(Path(url), htm)
        meta = url_base + str(pathname2url(htm))
        meta_dict = {"source_url": meta}
        print(htm)
        with open(Path(to_open), encoding='UTF-8') as f:
            add_doc = discovery.add_document(env_id, collection_id, file=f, metadata=json.dumps(meta_dict), filename=meta).get_result()
            print(json.dumps(add_doc, indent=4))

# To get stopwords from a collection

def getStopWordStatus(env_id, collection_id = None):
    """
    params: Environment ID and Collection ID
    returns: Details of available stopword list in JSON
    """
    collection_id = collection_id if collection_id else input('Please specify collection ID: ')
    return discovery.get_stopword_list_status(env_id, collection_id)

# To add stopwords to a collection

def addStopWords(env_id, collection_id = None, sw_file = None, sw_file_name = None):
    """
    params: Environment ID, Collection ID, Stopword File, Stopword File name (optional, 'None' by default)
    returns: Details of the ingested stopword file as JSON
    """
    collection_id = collection_id if collection_id else input('Please specify collection ID: ')
    sw_file = sw_file if sw_file else input('Please enter path for the stopword file: ')
    sw_file = Path(sw_file)
    with open(sw_file) as swf:
        return discovery.create_stopword_list(env_id, collection_id, swf, sw_file_name)

# To delete stopwords from a collection

def deleteStopWords(env_id, collection_id = None):
    """
    params: Environment ID, Collection ID
    returns: Details of the deleted stopword file as JSON
    """
    collection_id = collection_id if collection_id else input('Please specify collection ID: ')
    return discovery.delete_stopword_list(env_id, collection_id)

# To get expansions list status from a collection
def getExpansionListStatus(env_id, collection_id = None):
    """
    params: Environment ID and Collection ID
    returns: Details of available stopword list in JSON
    """
    collection_id = collection_id if collection_id else input('Please specify collection ID: ')
    return discovery.list_expansions(env_id, collection_id)

# To add stopwords to a collection

def addExpansionsList(env_id, expansionsJSON_path = None, collection_id = None):
    """
    params: Environment ID, Expansions JSON path (loads), Collection ID (optional, 'None' by default)
    returns: Details of the expansions as JSON
    """
    collection_id = collection_id if collection_id else input('Please specify the appropriate collection ID: ')
    with open(Path(expansionsJSON_path)) as expansions:
            expansion_list = json.load(expansions)
            return discovery.create_expansions(env_id, collection_id, expansion_list['expansions'])

# To delete stopwords from a collection

def deleteExpansionsList(env_id, collection_id = None):
    """
    params: Environment ID, Collection ID
    returns: Details of the deleted expansions list as JSON
    """
    collection_id = collection_id if collection_id else input('Please specify the appropriate collection ID: ')
    return discovery.delete_expansions(env_id, collection_id)

# To query discovery (NLQ)

def queryDiscovery(env_id, collection_id, query):
    """
    params: query string
    returns: query response as JSON
    """
    return discovery.query(
        environment_id = env_id,
        collection_id = collection_id,
        natural_language_query = query,
        count = 1,
        passages = True,
        return_fields  ="text",
        passage_count = 3,
        passage_characters = 1000
    )

# To list training data

def listTrainingData(env_id, collection_id):
    return discovery.list_training_data(env_id, collection_id)

# To delete training data

def deleteTrainingData(env_id, collection_id):
    collection_id = collection_id if collection_id else input('Please input collection ID: ')
    return discovery.delete_all_training_data(env_id, collection_id)

# Fallback for program

def fallback(src, item = None):
    
    if src == 'start' or src == 'train':
        print('Unexpected argument - {} | Atmost 2 kwargs expected'.format(item))
    
    elif src == 'action':
        print('please provide \'action_item\'')
    
    elif src == 'action_item':
        print('please provide \'action\'')
    
    elif src == 'bad sw':
        print('Ivalid use of start flag')
    
    elif src == 'list':
        print('please provide item to list')

    else:
        print('Ivalid kwargs, please refer help..')

    exit()

# To start the training process

def train(env_id, xl_path, COLLECTION_ID = None, alert = None):

    if alert and not None:
        train_alert = str(input('Do you want to train discovery? (Y/N): '))
        if train_alert == 'N' or train_alert == 'n' or train_alert == 'No' or train_alert == 'no':
            print('Exiting program..')
            exit()
        elif train_alert == 'Y' or train_alert == 'y' or train_alert == 'Yes' or train_alert == 'yes':
            train(xl_path, COLLECTION_ID, False)
        else:
            print('Invalid input.. Please provide \'Y\' or \'N\'')
            train(xl_path, COLLECTION_ID, True)

    else:
        COLLECTION_ID = COLLECTION_ID if COLLECTION_ID else 'aa479e91-1647-4c5a-b98d-57f01e7386d8'

        # List Training Data
        # print(listTrainingData(env_id, COLLECTION_ID))

        # Delete Exisiting Training data if exists and create new
        print(deleteTrainingData(env_id, COLLECTION_ID))
    
        # Load workbook and worksheet
        wb = load_workbook(xl_path)
        ws = wb['Sheet1']

        # Get total records in the worksheet
        dimensions = ws.calculate_dimension()
        ROWS = int(dimensions.split('A1:D')[1])
        
        # since format has only 4 columns by default
        COLS = 4
        
        # Get Excel data
        xl_json = xli(ws, ROWS, COLS)

        # Get Discovery document mapping
        disc_json = wtu.listAllDocuments(API_KEY, API_URL, env_id, COLLECTION_ID)

        # Get the Relevancy training dictionary
        training_json = wtu.watsonJSONgenerator(xl_json, disc_json, env_id, COLLECTION_ID)
        
        print('training watson discovery..')
        # print(json.dumps(training_json, indent=4))

        for index, key in enumerate(training_json):

            # If watson API dictionary exists
            if key[index + 1].get('natural_language_query') is not None or key[index + 1].get('examples') is not None:
                print('{} query is \"{}\" and has {} example(s)'.format(index + 1, key[index+1].get('natural_language_query'), len(key[index+1].get('examples'))))
                discovery.add_training_data(
                    environment_id = key[index + 1].get('environment_id'),
                    collection_id = key[index + 1].get('collection_id'),
                    natural_language_query = key[index + 1].get('natural_language_query'),
                    filter = None,
                    examples = key[index + 1].get('examples')
                )
            else:
                print('Skipping dirty query..')
                pass

# Check existence of collection in environment

def getCollectionID(env_id):
    cugid = cfaqid = None

    print('Available Collections..\n-----------------------------------------')
    collections = listCollections(env_id)
    collections = collections.get('collections')
    
    for collection in collections:
        if collection.get('name') == 'Central User Guide':
            cugid = collection.get('collection_id')
        if collection.get('name') == 'Central FAQs':
            cfaqid = collection.get('collection_id')
    
    if cugid is not None and cfaqid is not None:
        collection_exists = True
    else:
        collection_exists = False

    return cugid, cfaqid, collection_exists

# Check existence of configuration in environment

def getConfigurationID(env_id):
    cugConfig = cfaqConfig = config_exists = None
    
    print('Available Configurations..\n-----------------------------------------')
    configs = listConfig(env_id)
    configs_list = configs['configurations']
    
    for config in configs_list:
        if config['name'] == 'Central User Guide Configuration':
            cugConfig = config.get('configuration_id')
        if config['name'] == 'Central FAQs and Terms Configuration':
            cfaqConfig = config.get('configuration_id')
    
    if cugConfig is not None and cfaqConfig is not None:
        config_exists = True
    else:
        config_exists = False

    return cugConfig, cfaqConfig, config_exists

# To start the entire workflow

def startWorkflow(env_id, xl_path, train_alert):
    
    cugConfig, cfaqConfig, config_exists = getConfigurationID(env_id)
    # Create config if it doesn't exist
    """
    ADD CONFIGURATION NOT WORKING THROUGH PYTHON SDK - MANUALLY ADDED THROUGH CURL
    example:
        curl -X POST -u "apikey":"{apikey}" -H "Content-Type: application/json" -d @{file.json} "https://gateway-wdc.watsonplatform.net/discovery/api/v1/environments/{environment_id}/configurations?version=2019-04-30"
    """
    if config_exists:
        print('\n{} -> Central User Guide Configuration\n{} -> FAQs / Terms Configuration\n'.format(cugConfig, cfaqConfig))
    
    if not config_exists:
        config_paths = ['user_guide_config.json', 'faq_config.json']
        
        for config_path in config_paths:
            cmd = 'curl -X POST -u "apikey":"'+ API_KEY +'" -H "Content-Type: application/json" -d @'+ config_path +' "https://gateway-wdc.watsonplatform.net/discovery/api/v1/environments/'+ env_id +'/configurations?version=2019-04-30"'
            print('Executing cURL..\n-----------------------------------------\n{}\n-----------------------------------------'.format(cmd))
            curl = subprocess.call(cmd, shell = True)
            print('\n---CURL---\nCODE: {}\n-----------------------------------------'.format(curl))

        cugConfig, cfaqConfig, config_exists = getConfigurationID(env_id)

    cugid, cfaqid, collection_exists = getCollectionID(env_id)
    
    # Delete Existing collection
    if collection_exists:
        deleteCollection(env_id, cugid)
        deleteCollection(env_id, cfaqid)
        collection_exists = False

    # Create two collections
    if not collection_exists:

        # Create Central User Guide and Central FAQs collections
        print('Creating Collections..\n-----------------------------------------')
        createCollection(env_id, name = 'Central User Guide', desc = 'Testing python utils')
        createCollection(env_id, name = 'Central FAQs', desc = 'Testing python utils')
        print('Finished creating collections in {0:.2g}s..\n'.format(time.time() - start_time))

        cugid, cfaqid, collection_exists = getCollectionID(env_id)
        print('-----------------------------------------\n{} is the Central User Guide Collection\n{} is the Central FAQs Collection\n-----------------------------------------'.format(cugid, cfaqid))

        # Apply configuration to those collections
        print('Updating collections with configuration..\n-----------------------------------------')
        updateCollection(env_id, cugid, cugConfig, name = 'Central User Guide', flag = True)
        updateCollection(env_id, cfaqid, cfaqConfig, name = 'Central FAQs', flag = True)
        print('Finished updating collections in {0:.2g}s..\n'.format(time.time() - start_time))
        
        # Upload Documents | S3 Bucket files
        print('Uploading documents to collections..\n-----------------------------------------')
        tfaq_files = [{
            "source": 'C:/Users/manikvig/Documents/search fiddle/terms/faqs.htm',
            "meta": 'https://help.central.arubanetworks.com/latest/documentation/online_help/content/faqs.htm',
            "filename": 'faqs.htm'
        }, {
            "source": 'C:/Users/manikvig/Documents/search fiddle/terms/terms_a.htm',
            "meta": 'https://help.central.arubanetworks.com/2.4.8/documentation/online_help/content/common%20files/topic_files/terms.htm',
            "filename": 'terms.htm'
        }, {
            "source": 'C:/Users/manikvig/Documents/search fiddle/terms/terms_b.htm',
            "meta": 'https://help.central.arubanetworks.com/2.4.8/documentation/online_help/content/common%20files/topic_files/terms.htm',
            "filename": 'terms.htm'
        }]
        
        for fo in tfaq_files:
            with open(Path(fo['source']), encoding='UTF-8') as f:
                add_doc = discovery.add_document(env_id, cfaqid, file=f, metadata = json.dumps({"source_url": fo['meta']}), filename = fo['filename']).get_result()
                print(json.dumps(add_doc, indent=4))
        print('Finished uploading documents to FAQs collection {0:.2g}s..\n'.format(time.time() - start_time))

        docs = s3u.uploadS3toDiscovery()
        for doc in docs:
            print(json.dumps(discovery.add_document(env_id, cugid, file = doc['data'], filename = doc['meta'], metadata = json.dumps(doc['meta'])).get_result(), indent = 4))
        print('Finished uploading documents from s3 in {0:.2g}s..\n'.format(time.time() - start_time))
        
        # To upload from local directory
        # uploadLocalDocumentsToDiscovery(Path('C:/Users/manikvig/Desktop/content'), '\w*\.htm', 'https://help.central.arubanetworks.com/latest/documentation/online_help/content/', env_id, cugid)

        # Begin training
        # train(env_id, xl_path, cugid, train_alert)
        # print('Finished training in {0:.2g}s..\n'.format(time.time() - start_time))

        # Upload stopwords to Central User Guide
        print('Uploading stopwords..\n-----------------------------------------')
        print(addStopWords(ENV_ID, cugid, 'C:/Users/manikvig/Documents/Work/AI Search/discovery-file-upload/Assets/stopwords.txt', 'Test Stopwords for CUG'))
        print('Finished uploading stopwords in {0:.2g}s..\n'.format(time.time() - start_time))

        # Upload Expansions List
        print('Uploading Expansions List..\n-----------------------------------------')
        print(addExpansionsList(ENV_ID, cugid))

if __name__ == "__main__":

    # instance creds
    API_KEY = '<YOUR_API_KEY>'
    ENV_ID = '<YOUR_ENVIRONMENT_ID>'

    API_URL = '<YOUR_API_URL>'
    COLLECTION_ID = ''
    XL_PATH = '<EXCEL_SHEET_PATH>'
 
    discovery = DiscoveryV1(
        version="<VERSION>",
        url = API_URL,
        iam_apikey = API_KEY
    )

    # Creating CLI for Discovery Utility
    parser = argparse.ArgumentParser(description = 'Python utility for IBM Watson Discovery\nYou can create or delete collection(s) or configuration(s)', epilog = u"\N{COPYRIGHT SIGN} Aruba Networks")
    
    """
    Workflow flag - used to start the workflow
        1. Create a collection
        2. Add configurationD
        3. Fetch files from S3 bucket and upload to collection

    Training flag (optional) - used to start relevancy training in given collection
    """
    parser.add_argument('-sw', '--start', default = False, action = 'store_true', help = 'Begins the workflow')
    parser.add_argument('-t', '--train', default = False, action = 'store_true', help = 'Asks to train discovery')
    
    """
    Optional | Mutually Exclusive flags

    Action -> Create, Read, Update, Delete
    Action Items -> Collection, Configuration
    """
    action = parser.add_mutually_exclusive_group()
    
    # What operation to do?
    action.add_argument('-action', '--action', default = None, choices = ['create', 'update', 'delete'], type = str, help = 'operation specification - CRUD')
    action.add_argument('-list', '--list', default = None, choices = ['all', 'one'], help = 'list collections / configs')

    # On which item the operation is to be done?
    action_item = parser.add_mutually_exclusive_group()
    action_item.add_argument('-collection', dest = 'collection', default = False, action = 'store_true', help = 'Collection Item')
    action_item.add_argument('-config', dest = 'config', default = False, action = 'store_true', help = 'Configuration Item')
    action_item.add_argument('-stopwords', dest = 'stopwords', default = False, action = 'store_true' , help = 'Stopwords Item')
    action_item.add_argument('-expansions', dest = 'expansions', default = False, action = 'store_true' , help = 'Expansions Item')
    
    #  Parse keyword arguments
    args = parser.parse_args()

    # Exit program if no arguments are provided
    if args.action == None and (args.collection if args.collection else args.config) == False and args.list == None and args.start == False and args.train == False:
        print('No kwargs provided')
        exit()
    else:
        print('Provided **kwargs -> {}\n'.format(args))
    
    # Workflow management code
    if args.start:
        
        # Fallback if any action or action item is specified 
        args.action != None and fallback('start' if args.start else 'train', args.start if args.start else args.train)
        (args.collection or args.config) and fallback('train' if args.train else 'start', args.train if args.train else args.start)

        # Start workflow
        args.start and not args.train and startWorkflow(ENV_ID, XL_PATH, True)
        args.start and args.train and startWorkflow(ENV_ID, XL_PATH, False)
        
    # Train discovery
    elif args.train:
        args.train and train(ENV_ID, Path(XL_PATH), COLLECTION_ID, False)

    # List collection / configuration / stopwords
    elif args.list:
        
        if args.start:
            fallback(None, 'bad sw')
        
        else:
            if args.collection:
                args.list == 'all' and listCollections(ENV_ID)
                args.list == 'one' and getCollection(ENV_ID)
            
            elif args.config:
                args.list == 'all' and listConfig(ENV_ID)
                args.list == 'one' and getConfig(ENV_ID)
            
            elif args.stopwords is not None:
                print(json.dumps(getStopWordStatus(ENV_ID), indent = 4))

            elif args.expansions is not None:
                print(json.dumps(getExpansionListStatus(ENV_ID), indent = 4))

            else:
                fallback('list')

    # CRUD for action items
    elif args.action and (args.collection or args.config or args.stopwords) and args.start == False:
        
        if args.collection:
            
            if args.action == 'create':                
                createCollection(ENV_ID)
            
            if args.action == 'delete':
                deleteCollection(ENV_ID)
            
            if args.action == 'update':
                updateCollection(ENV_ID)
            
        if args.config:
            
            if args.action == 'create':                
                createConfig(ENV_ID)
            
            if args.action == 'delete':
                deleteConfig(ENV_ID)
            
            if args.action == 'update':
                updateConfig(ENV_ID)

        if args.stopwords:
            
            if args.action == 'create':                
                createConfig(ENV_ID)
            
            if args.action == 'delete':
                deleteConfig(ENV_ID)
            
            if args.action == 'update':
                print('Sorry you cannot update a stopword list..\nExiting program..')
                exit()
    
    else:
        
        if args.start:
            fallback('bad sw', args.start)
        
        if args.action or (args.collection or args.config or args.stopwords):
            fallback('action' if args.action else 'action_item', args.action if args.action else (('Collection Item' if args.collection else 'Config Item')) if (args.collection or args.config) else 'Stopwords Item')

# End timer
print('Finished in {0:.2g}s..'.format(round((time.time() - start_time) % 60)))