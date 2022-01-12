import json
import urllib.parse
import boto3
from pprint import pprint
from requests_aws4auth import AWS4Auth
import requests
from time import strptime
import logging 
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

USER = "kt"
PW = "shreK@!$799"
print('Loading function')

s3 = boto3.client('s3')
rek = boto3.client('rekognition')
# opensearch = boto3.client('opensearch')

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    print('event here')
    pprint(event)
    print('event there')
    bucket = event['Records'][0]['s3']['bucket']['name']
    photo_key = (event['Records'][0]['s3']['object']['key'])
    print(bucket)
    logger.debug("bucket")
    logger.debug(bucket)
    logger.debug("photo key")
    logger.debug(photo_key)
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        print('eventttt')
        print(event)
        response = s3.get_object(Bucket=bucket, Key=key)
        print("S3 response")
        print(response)
        # since lambda gets triggered upon PUT event we should get the correct S3 object 
        
        createdTimestamp = response["ResponseMetadata"]["HTTPHeaders"]["last-modified"] 
        s = createdTimestamp[5:-4] # removing day of week at the beginning and GMT at the end
        day = s[:2]
        month = s[3:6]
        year = s[7:11]
        time = s[-8:]
        month = str(strptime(month,'%b').tm_mon)
        createdTimestamp = year + "-" + month + "-" + day + "T" + time
        # we are actually using last modified as the timestamp 
        print(createdTimestamp)
        
        rek_labels = rekognition_detect_labels(bucket, photo_key)["Labels"]
        rek_labels = [r["Name"] for r in rek_labels]
        print("Rekognition labels")
        print(rek_labels)
        head_obj = head_object(bucket, photo_key)
        if 'x-amz-meta-customlabels' in head_obj['ResponseMetadata']['HTTPHeaders']: 
            meta_labels = head_obj['ResponseMetadata']['HTTPHeaders']['x-amz-meta-customlabels']
            meta_labels = meta_labels.split(',')
        else: 
            meta_labels = []
        A1 = meta_labels # supposed to be a JSON array 
        print("A1")
        print(rek_labels)
        
        store_in_opensearch(bucket, photo_key, A1+rek_labels, createdTimestamp)
        
        print("CONTENT TYPE: " + response['ContentType'])
        return response['ContentType']
        
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e

def rekognition_detect_labels(bucket, photo_key): 
    response = rek.detect_labels(
        Image={
            'S3Object': {
                'Bucket': bucket,
                'Name': photo_key
                # 'Name': 'golden-retriever-royalty-free-image-506756303-1560962726.jpeg'
            }
        },
        # MaxLabels=3 # no limit on the number of labels -- set limit on confidence threshold instead
        MinConfidence=75
    )
    return response
    
def head_object(bucket, photo_key): 
    response = s3.head_object(
        Bucket=bucket,
        Key=photo_key
    )
    return response
    
def store_in_opensearch(bucket, photo_key, labels, createdTimestamp): 
    """
        Based on https://docs.aws.amazon.com/opensearch-service/latest/developerguide/integrations.html#integrations-s3-lambda
    """
    # create JSON object according to schema
    # print(photo_key)
    # print(bucket)
    # print(createdTimestamp)
    # print(labels)
    document = {
        "objectKey": photo_key,
        "bucket": bucket, 
        "createdTimestamp": createdTimestamp, 
        "labels": labels
    }
    
    # store JSON object in opensearch index ("photos")
    region='us-east-1'
    service='es'
    credentials=boto3.Session().get_credentials()
    # awsauth=AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    awsauth = (USER, PW)
    host = "https://search-photos-c7odzutlqzixzrpkf5y2mlpa5q.us-east-1.es.amazonaws.com"
    index = 'lambda-s3-index'
    type = '_doc'
    url = host + '/' + index + '/' + type + '/' + photo_key
    headers = { "Content-Type": "application/json" }
    r = requests.put(url, auth=awsauth, json=document, headers=headers)
    print("json format right here")
    pprint(r.json())
    
# { "index" : { "_index": "photos", "_id" : photo_key } }
# {"objectKey": photo_key, "bucket": bucket, "createdTimestamp": createdTimestamp, "labels": labels}
