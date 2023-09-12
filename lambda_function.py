import boto3
import os
import sys
import uuid
from urllib.parse import unquote_plus
from PIL import Image
import PIL.Image

s3_client = boto3.client('s3')

def resize_image(image_path, dimensions, bucket):
    with Image.open(image_path) as image:
        for width, height in dimensions:
            # Generate a unique key for each resized image
            resized_key = f'resized/{width}x{height}/{os.path.basename(image_path)}'
            
            # Resize the image
            resized_image = image.resize((width, height))
            
            # Save the resized image to /tmp/
            resized_image_path = f'/tmp/{os.path.basename(image_path)}-{width}x{height}.jpg'
            resized_image.save(resized_image_path, 'JPEG')
            
            # Upload the resized image to S3
            s3_client.upload_file(resized_image_path, bucket, resized_key)

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        download_path = '/tmp/{}'.format(key)
        
        # Download the image
        s3_client.download_file(bucket, key, download_path)
        
        # Define the desired dimensions for resizing
        dimensions = [(100, 100), (200, 200), (400, 400)]
        
        # Resize the image to multiple dimensions and save them
        resize_image(download_path, dimensions, bucket)
