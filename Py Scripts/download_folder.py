# Jay AWS bucket
# Download a complete folder

import boto3
import os
import botocore
import json
from watson_developer_cloud import DiscoveryV1
# import xlsxwriter

files_from_IBM_Discovery = []
files_from_IBM_Discovery_copy = []
files_from_S3_bucket = []

# AWS credentials
aws_access_key_id = 'AKIAICVV2OPBSEUFEKMQ'
aws_secret_access_key = '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'
aws_bucket = 'help.central.arubanetworks.com'

# IBM discovery credentails
API_key = 'gTAsSzZBIxtS_p5g1-JBIjfeXs0F2a0DtOZI7YAzO2Hk'
discovery_url = 'https://gateway-wdc.watsonplatform.net/discovery/api'
env_id = '7206305c-d647-41f2-a1cc-eb909ec2c641'


# creating boto object
s3 = boto3.resource('s3',
aws_access_key_id= aws_access_key_id,
aws_secret_access_key= aws_secret_access_key)

# creating IBM discovery object
discovery = DiscoveryV1(
    version="2019-03-25",
    iam_apikey= API_key,
    url=discovery_url
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
        '7206305c-d647-41f2-a1cc-eb909ec2c641',
        'faadff2c-ddcc-41e4-84aa-2aa9c40f3b09',
        query = "*.*"
    )
    all_documents = response.result["results"]
    files_from_IBM_Discovery = tuple(map(lambda document_item:[document_item["extracted_metadata"]["filename"], document_item["id"]],all_documents))
    print(files_from_IBM_Discovery)
    # workbook = xlsxwriter.Workbook('discovery_collection.xlsx')
    # worksheet = workbook.add_worksheet("My sheet") 
    # row = 0
    # col = 0
    # for doc_id, doc_name in (files_from_IBM_Discovery): 
    #     worksheet.write(row, col, doc_id) 
    #     worksheet.write(row, col + 1, doc_name) 
    #     row += 1
    # workbook.close()  
    getReport(files_from_IBM_Discovery_copy)


def getReport(files_from_IBM_Discovery_copy):
    updatedFiles=[]
    addedNewly=[]
    deleted=[]
    print("building report")
    for S3_item in files_from_S3_bucket:
        found_in_discovery_collecton = False
        for IBM_dicovery_item in files_from_IBM_Discovery_copy:
            # print(S3_item +"   " + IBM_dicovery_item[0])
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

# result_metadata


# Downloads all files from AWS and puts it into IBM Dicovery
my_bucket = s3.Bucket(aws_bucket)

# 1. Gets all files from AWS bucket
# 2. Downloads files individually
def getAllFiles():
    print("Starting Get all files from S3 bucket")
    file_count = 0
    for file in my_bucket.objects.all():
        file_path = str(file.key)
        if(file_path.endswith('.htm')):
            file_name = file_path.split('/')[-1]
            files_from_S3_bucket.append(file_name)
            # read the excel file and get the document id for the file

            # downloadFile(file.key,str(file_count))
            file_count = file_count+1
    # print(file_count)
    print(files_from_S3_bucket)


# add_document(self, environment_id, collection_id, file=None, metadata=None, file_content_type=None, filename=None, **kwargs)




#  Downloads the files
def downloadFile(filePath,file_count):
    print("getting file")
    print(filePath)
    try:
        s3.Bucket('aws-codestar-us-west-2-459262888907').download_file(filePath,file_count)
        print("downloaded successfully")
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] =='404':
            print('The object doesnot exist')
        else:
            raise


getAllFiles()            
# setupCollectionsAndConfigurations()
