import boto3
import json

def lambda_handler(event, context):
    s3_client = boto3.client('s3')
    rekognition_client = boto3.client('rekognition')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ImageMetadata')

    # Get bucket name and key from the S3 event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Read the image file from S3
    response = s3_client.get_object(Bucket=bucket, Key=key)
    image_content = response['Body'].read()

    # Validate image format
    if not key.lower().endswith(('.png', '.jpg', '.jpeg')):
        raise ValueError("NotSupportedImageType")

    # Process with Rekognition for Object Detection
    rekog_response = rekognition_client.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': key}})

    # Extract labels and store them in DynamoDB
    labels = [label['Name'] for label in rekog_response['Labels']]
    table.put_item(Item={'Filename': key, 'Labels': json.dumps(labels)})

    # Further processing steps...

    return {
        'statusCode': 200,
        'body': json.dumps('Process completed successfully.')
    }
