from excel_parser import xl_iterator as xli
from openpyxl import  load_workbook, Workbook
import json
from pathlib import Path
from watson_developer_cloud import DiscoveryV1

def listAllDocuments(api_key, api_url, env_id, collection_id):
    """
    params: KEY, URL, ENVIRONMENT ID, COLLECTION ID
    returns: Dictionary with { Meta: ID } mapping
    """

    discovery = DiscoveryV1(
        version = "2019-03-25",
        iam_apikey = api_key,
        url = api_url
    )
    
    response = discovery.query(env_id, collection_id, query = "*.*", count = 400)
    all_documents = response.result["results"]
    
    files_from_IBM_Discovery = dict(
        map(
            lambda document_item:[document_item["extracted_metadata"]["filename"], document_item["id"]], all_documents
            )
        )

    return files_from_IBM_Discovery


def getSourceDocID(source, disc_dict):
    
    discovery_keys = list(disc_dict.keys())

    for discovery_key in discovery_keys:
        if str(discovery_key).find(str(source).lower()) > -1:
            return str(disc_dict.get(discovery_key))
    
    else:
        return False

def watsonJSONgenerator(xl_json, disc_dict, env_id, collection_id):
    """
    Generates the training data JSON file

    params: Excel JSON, Discovery JSON, ENVIRONMENT ID, COLLECTION ID
    returns: A dictionary that can be used for Discovery 'Relevancy Training'
    """
    
    training_json = []
    count = 0

    for key in xl_json.keys():

        sources = xl_json[key]['sources']
        questions = xl_json[key]['questions']
        relevance = xl_json[key]['relevance']

        # For each question, validate source
        for question in questions:
            count += 1
            watson_api_json = {
                "environment_id": env_id,
                "collection_id": collection_id,
                "natural_language_query": "",
                "examples": []
            }

            # Discard nbsp in parsed unicode
            question = question.replace('\u00a0', ' ')
            
            index = 0
            
            watson_api_json.update({
                'natural_language_query': question
            })
            
            for source in sources:
                doc_id = getSourceDocID(source, disc_dict)
                if doc_id != False:
                    watson_api_json['examples'].append({
                        'document_id': doc_id,
                        'cross_reference': '',
                        'relevance': relevance[index]
                    })
                    index += 1
            
            training_json.append({
                count: watson_api_json
            })
    
    return training_json