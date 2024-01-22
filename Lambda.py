# serializeImageData Function
# --------------------------------------------------

import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input
    key = event.get('s3_key') ## TODO: fill in
    bucket = event.get('s3_bucket') ## TODO: fill in
    
    # Download the data from s3 to /tmp/image.png
    s3.download_file(bucket, key, '/tmp/image.png') ## TODO: fill in
    
    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }

# classifierModel Function
# --------------------------------------------------
import json
import boto3
import base64

# Fill this in with the name of your deployed model
ENDPOINT = "image-classification-2023-09-28-18-31-07-174" 
#session= session.Session()
runtime = boto3.Session().client('sagemaker-runtime')

def lambda_handler(event, context):

    # Decode the image data
    image = base64.b64decode(event['body']['image_data'])
    
    #envoke the endpoint using boto3 runtime
    response = runtime.invoke_endpoint(EndpointName=ENDPOINT, ContentType='image/png', Body=image)
    predictions = json.loads(response['Body'].read().decode())
    
    # We return the data back to the Step Function #Create a new key to the event named   "inferences"  
    event['body']["inferences"] = predictions
    
    #print(json.dumps(event))
    
    return {
        'statusCode': 200,
        'body': event

        }

# filterInferences Function
# --------------------------------------------------
import json


THRESHOLD = .7


def lambda_handler(event, context):
    
    # Grab the inferences from the event
    # Access 'body' and parse it to dict if it is a string
    body = event.get('body', {})
    if isinstance(body, str):
        body = json.loads(body)
    
    # Access 'body' within the first 'body' and parse it to dict if it is a string
    inner_body = body.get('body', {})
    if isinstance(inner_body, str):
        inner_body = json.loads(inner_body)
    
    # Grab the inferences from the inner_body
    inferences = inner_body.get('inferences', []) ## TODO: fill in
    
    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = any(inference >= THRESHOLD for inference in inferences) ## TODO: fill in
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }