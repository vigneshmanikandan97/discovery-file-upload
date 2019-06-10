import boto3
import os
import botocore
import json
from watson_developer_cloud import DiscoveryV1
from io import StringIO as sio

files_from_IBM_Discovery = []
files_from_IBM_Discovery_copy = []
files_from_S3_bucket = []

# AWS credentials
aws_access_key_id = 'AKIASZOVVKFBPQUTHB47'
aws_secret_access_key = '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'
aws_bucket = 'help.central.arubanetworks.com'

# IBM discovery credentails
API_key = 'bEyrHwAUKTw4pwmehUFyQ1SYLD7ubOLPnTU3iXTOkVNW'
discovery_url = 'https://gateway-wdc.watsonplatform.net/discovery/api'
env_id = 'c545c99f-aced-48b1-b3ef-fa498bfedeb7'

# creating boto object
s3 = boto3.resource('s3', aws_access_key_id= aws_access_key_id, aws_secret_access_key= aws_secret_access_key)
client = s3.meta.client

# creating IBM discovery object
discovery = DiscoveryV1(
    version = "2019-03-25",
    iam_apikey = API_key,
    url = discovery_url
)

# check if collection exists
def setupCollectionsAndConfigurations():
    collections = discovery.list_collections(env_id)
    print("Getting all collections")
    
    all_collections = list(map(lambda collection:[collection['name'],collection['configuration_id']],collections.result.get("collections")))
    print(all_collections)
    
    listAllDocuments()

# get all file name with document_id from Discovery and store in excel file
def listAllDocuments():
    print('Getting all document with name and IDs from Discovery')
    
    response = discovery.query(
        'c545c99f-aced-48b1-b3ef-fa498bfedeb7',
        'a491da59-17d1-4ba4-ab9f-b725c9eee4f5',
        query = "*.*"
    )
    
    all_documents = response.result["results"]
    files_from_IBM_Discovery = tuple(map(lambda document_item:[document_item["extracted_metadata"]["filename"], document_item["id"]],all_documents))
    
    print(files_from_IBM_Discovery)
    getReport(files_from_IBM_Discovery_copy)

# Generates delta
def getReport(files_from_IBM_Discovery_copy):
    updatedFiles=[]
    addedNewly=[]
    deleted=[]
    print("Generating report..")
    
    for S3_item in files_from_S3_bucket:
        found_in_discovery_collecton = False
        
        for IBM_dicovery_item in files_from_IBM_Discovery_copy:
        
            if S3_item == IBM_dicovery_item[0]:
                found_in_discovery_collecton = True
                updatedFiles.append(IBM_dicovery_item)
        
        if not found_in_discovery_collecton:
            addedNewly.append(files_from_S3_bucket)
    
    if(len(files_from_IBM_Discovery_copy)>0):
        deleted = files_from_IBM_Discovery_copy

    print(len(updatedFiles), "  files were updated")    
    print(len(addedNewly), "  files were added")
    print(len(deleted), "  files were deleted")

# Downloads all files from AWS and puts it into IBM Dicovery
my_bucket = s3.Bucket(aws_bucket)
bucket_prefix = 'latest/documentation/online_help/content'

# 1. Gets all files from AWS bucket
# 2. Downloads files individually
def getAllFiles():
    print("Accessing S3 Bucket..")
    file_count = 0
    
    for file in my_bucket.objects.filter(Prefix = bucket_prefix):
        
        file_path = str(file.key)
        
        if(file_path.endswith('.htm')):
            
            file_name = file_path.split('/')[-1]
            files_from_S3_bucket.append(file_name)
            downloadFile(file_path, str(file_name))
            file_count = file_count + 1
    
    print('{} files found on S3 bucket'.format(file_count))

#  Downloads the files
def downloadFile(file_path, file_name):
    
    try:
        print('Downloading \"{}\"..'.format(file_name))
        obj = client.get_object(Bucket = aws_bucket, Key = file_path)
        data = sio(obj.get('Body').read().decode('utf-8'))
        meta = {
        "source": file_path
        }
        discovery.add_document(env_id, 'ee012b37-6897-43ea-8f6d-68337f754f35', file = data, filename = file_path, metadata = json.dumps(meta))
        print("success\n")
    
    except botocore.exceptions.ClientError as e:
        
        if e.response['Error']['Code'] =='404':
            print('The object doesn\'t exist')
        
        else:
            raise 'ObjectNotFoundException'

getAllFiles()
setupCollectionsAndConfigurations()
