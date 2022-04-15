import os
import boto3

AMI = os.environ['AMI']
INSTANCE_TYPE = os.environ['INSTANCE_TYPE']
KEY_NAME = os.environ['KEY_NAME']
SUBNET_ID = os.environ['SUBNET_ID']
REGION = os.environ['REGION']
BUCKET = os.environ['BUCKET']
TABLE = os.environ['TABLE']
ID = os.environ['ID']

ec2 = boto3.client('ec2', region_name=REGION)

def lambda_handler(event, context):
    init_script = f"""#!/bin/bash
                yum update -y
                yum install -y jq
                
                aws s3 cp s3://{BUCKET}/InputFile.txt filedata
                aws dynamodb get-item --table-name {TABLE} \
                --key '{{"Id":{{"N":"{ID}"}}}}' \
                --consistent-read \
                --projection-expression "input_text" \
                --return-consumed-capacity TOTAL > input.json \
                
                jq '.input_text' input.json > input_text
                (cat filedata; echo ':'; cat input_text) > outputdata
                (echo '{{ "input_text":'; cat input_txt; echo ', "output_file_path": "{BUCKET}/OutputFile.txt"}}') > output.json
                
                aws s3 cp data s3://{BUCKET}/OutputFile.txt
                aws dynamodb put-item \
                --table-name Thread \
                --item file://output.json \
                
                shutdown -h +5"""

    instance = ec2.run_instances(
        ImageId=AMI,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        SubnetId=SUBNET_ID,
        MaxCount=1,
        MinCount=1,
        InstanceInitiatedShutdownBehavior='terminate',
        UserData=init_script
    )

    instance_id = instance['Instances'][0]['InstanceId']
    return instance_id