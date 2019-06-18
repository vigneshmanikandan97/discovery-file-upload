import boto3
import botocore
import json
from io import StringIO as sio

# AWS credentials
aws_access_key_id = 'AKIASZOVVKFBPQUTHB47'
aws_secret_access_key = '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'
aws_bucket = 'help.central.arubanetworks.com'

# creating boto object
s3 = boto3.resource('s3', aws_access_key_id= aws_access_key_id, aws_secret_access_key= aws_secret_access_key)
client = s3.meta.client

# Downloads all files from AWS and puts it into IBM Dicovery
my_bucket = s3.Bucket(aws_bucket)
bucket_prefix = 'latest/documentation/online_help/content'

# 1. Gets all files from AWS bucket
# 2. Downloads files individually
def uploadS3toDiscovery():
    print("Accessing S3 Bucket..\nDownloading files from S3 and Uploading to Watson Discovery\n-----------------------------------------------------------")
    file_count = 0
    
    for file in my_bucket.objects.filter(Prefix = bucket_prefix):
        
        file_path = str(file.key)
        
        if (file_path.endswith('.htm')):
            
            file_name = file_path.split('/')[-1]
            if 'faqs.htm' not in file_name and 'terms.htm' not in file_name:
                try:
                    print('{}->Downloading \"{}\"..'.format(file_count + 1, file_name))
                    obj = client.get_object(Bucket = aws_bucket, Key = file_path)
                    data = sio(obj.get('Body').read().decode('utf-8'))
                    meta = {
                        "source_url": 'https://' + aws_bucket + '/' + file_path
                    }
                    yield {
                            "data": data,
                            "meta": meta
                        }
                
                except botocore.exceptions.ClientError as e:
                    
                    if e.response['Error']['Code'] =='404':
                        print('The object doesn\'t exist')
                    
                    else:
                        raise 'ObjectNotFoundException'
                
                file_count = file_count + 1
            
            else:
                continue
            
    print('\n{} files uploaded to Watson Discovery..'.format(file_count))
