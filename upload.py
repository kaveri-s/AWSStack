import boto3
import cgi
import io
import os

REGION = os.environ['REGION']

def lambda_handler(event, context):
    s3 = boto3.client('s3', region_name=REGION)
    dynamo = boto3.client('dynamodb', region_name=REGION)

    fp = io.BytesIO(event['body'].encode('utf-8'))
    pdict = cgi.parse_header(event['headers']['Content-Type'])[1]
    form_data = cgi.parse_multipart(fp, pdict)
    bucket = event['Records'][0]['s3']['bucket']['name']
    try:
        response = s3.generate_presigned_post(bucket, bucket+'/InputFile.txt', ExpiresIn = 3600)
        data = dynamo.put_item(
            TableName=event['Records'][0]['dynamo']['table']['name'],
            Item={
                'input_text': {
                    'S': form_data['text']
                },
                'input_file_path': {
                    'S': bucket+'/InputFile.txt'
                }
            }
        )
        return id
    except Exception as e:
        print(e)
        raise e
