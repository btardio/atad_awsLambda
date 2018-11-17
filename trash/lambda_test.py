import boto3
import lambda_function
import json

iam_client = boto3.client('iam')
lambda_client = boto3.client('lambda', region_name='us-east-1')

role = iam_client.get_role(RoleName='LambdaBasicExecution')

env_variables = dict() # Environment Variables

with open('projectEmailGraph.zip', 'rb') as f:
    zipped_code = f.read()

lambda_client.create_function(
  FunctionName='lambda_function.lambda_handler',
  Runtime='python3.6',
  Role=role['Role']['Arn'],
  Handler='lambda_handler',
  Code=dict(ZipFile=zipped_code),
  Timeout=300, # Maximum allowable timeout
  Environment=dict(Variables=env_variables),
)

test_event = { 
    "egyptsecurity": 
        [
            {
                "id": "201701010024",
                "year": "2017",
                "month": "1",
                "day":"1",
                "city": "Cairo",
                "lat":"30.084629",
                "lng":"31.334314",
                "type":"Bombing/Explosion",
                "target":"Unnamed Civilian/Unspecified"
            },
            {
                "id": "201701030038",
                "year": "2017",
                "month": "1",
                "day":"3",
                "city": "Ibsheway",
                "lat":"29.360998",
                "lng":"30.68244",
                "type":"Armed Assault",
                "target":"Police Patrol (including vehicles and convoys)"
            },
            {
                "id": "201701030050",
                "year": "2017",
                "month": "1",
                "day":"3",
                "city": "Alexandria",
                "lat":"31.200092",
                "lng":"29.918739",
                "type":"Armed Assault",
                "target":"Retail/Grocery/Bakery"
            }
        ]
    }


lambda_client.invoke(
        FunctionName='lambda_function',
        InvocationType='Event',
        Payload=json.dumps(test_event),
        )

