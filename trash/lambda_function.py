import json
import matplotlib as mp
import matplotlib._version


def lambda_handler(event, context):
    
    # Create a return dict
    rdict = matplotlib._version.get_versions()

    # Update the return dict with the hello string
    rdict.update({'greeting':'Hello from Lambda!'})
    
    return {
        'statusCode': 200,
        'body': json.dumps(rdict)
    }


