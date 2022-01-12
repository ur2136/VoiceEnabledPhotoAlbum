import json
import boto3
import datetime
import time
import os
import re
import dateutil.parser
import logging
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from pprint import pprint

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

USER = "kt"
PW = "shreK@!$799"
ELASTIC_SEARCH_DOMAIN = "search-photos-c7odzutlqzixzrpkf5y2mlpa5q.us-east-1.es.amazonaws.com"


def lambda_handler(event, context):
    # TODO implement
    
    lex_client= boto3.client('lex-runtime')
    lex_response = lex_client.post_text(
        botName = 'PhotoBotFinal',
        botAlias = 'PhotoBot',
        userId = 'sample',
        inputText = event['queryStringParameters']['q']
    )
    search = ""
    keyword_two = None
    logger.debug("keyword 1")
    logger.debug(lex_response)
    keyword_one = lex_response['slots']['keyword_one']
    logger.debug(keyword_one)
    search = keyword_one
    logger.debug(keyword_one)
    if ("keyword_two" in lex_response['slots'] and lex_response['slots']['keyword_two']):
        keyword_two = lex_response['slots']['keyword_two']
        search = search+" "+keyword_two
    logger.debug("keyword 2")
    logger.debug(keyword_two)
    logger.debug("search")
    logger.debug(search)
    
    # search starts here
    region='us-east-1'
    service='es'
    credentials=boto3.Session().get_credentials()
    awsauth=AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    
    client = OpenSearch(
        hosts = [{"host": ELASTIC_SEARCH_DOMAIN, "port": 443}], 
        http_auth = (USER, PW), 
        # http_auth = awsauth,
        use_ssl = True, 
        verify_certs = True, 
        connection_class = RequestsHttpConnection
    )
    print('s', search)
    query_terms = search.split(' ') # "cats dogs" turned to ["cats", "dogs"]
    print(query_terms)
    search_response = {"results": []}
    for query_term in query_terms: 
        # query_term = "Dog"
        if query_term[-1] == "s": # plural
            query_term = query_term[:-1]
        query = { # must modify query s.t. we have all the images are returned, not just 100 
            "size": 100, 
            "query": {
                "multi_match": {
                    "query": query_term
                }
            }
        }
        response = client.search(body=query)["hits"]["hits"]
        
        # https://ur2136-jk4534-b2.s3.amazonaws.com/golden-retriever-royalty-free-image-506756303-1560962726.jpeg
        for r in response: 
            # logger.debug(r)
            bucket = r["_source"]["bucket"]
            photo_name = r["_id"]
            url_ = "https://" + bucket + ".s3.amazonaws.com/" + photo_name
            labels_ = r["_source"]["labels"]
            search_response["results"].append({"url": url_, "labels": labels_})
        # must format response since we may have multiple 
        # search_response["results"].append({"url": "", "labels": ["", "", ""]})
        
    # search ends here
    logger.debug(search_response)
    print('search response')
    pprint(search_response)

    return {
        'statusCode': 200,
        'body': json.dumps(search_response),
        'headers': {
            'Content-Type':'application/json',
            'Access-Control-Allow-Origin':'*'
        }
    }
    
