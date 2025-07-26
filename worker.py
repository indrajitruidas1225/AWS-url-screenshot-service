import boto3
import json
import time
import uuid
from playwright.sync_api import sync_playwright

sqs = boto3.client('sqs', region_name='your-region')
s3 = boto3.client('s3', region_name='your-region')

QUEUE_URL = 'https://sqs.<region>.amazonaws.com/<account-id>/screenshot-requests'
BUCKET_NAME = 'your-s3-bucket-name'

def take_screenshot(url, file_path):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        page.screenshot(path=file_path)
        browser.close()

while True:
    print("Polling SQS...")
    response = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10
    )

    messages = response.get('Messages', [])
    if not messages:
        continue

    for msg in messages:
        try:
            body = json.loads(msg['Body'])
            url = body['url']
            file_name = f"{uuid.uuid4()}.png"
            local_path = f"/tmp/{file_name}"

            print(f"Taking screenshot of {url}...")
            take_screenshot(url, local_path)

            print("Uploading to S3...")
            s3.upload_file(local_path, BUCKET_NAME, file_name)

            print(f"Uploaded to https://{BUCKET_NAME}.s3.amazonaws.com/{file_name}")

            # Delete the message from the queue
            sqs.delete_message(
                QueueUrl=QUEUE_URL,
                ReceiptHandle=msg['ReceiptHandle']
            )
        except Exception as e:
            print("Error:", e)
