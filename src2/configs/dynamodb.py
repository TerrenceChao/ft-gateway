import boto3
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


dynamodb = boto3.resource("dynamodb")
