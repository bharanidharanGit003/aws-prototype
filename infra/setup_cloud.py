import boto3
import os
from shared.constants import DATA_LAKE_BUCKET

def setup_cloud():
    print("🚀 Starting SignalWorks Cloud Setup...")
    
    # 1. Create S3 Bucket
    s3 = boto3.client('s3')
    try:
        s3.create_bucket(Bucket=DATA_LAKE_BUCKET)
        print(f"✅ S3 Bucket '{DATA_LAKE_BUCKET}' created.")
    except Exception as e:
        print(f"ℹ️ S3 Bucket notice: {str(e)}")

    # 2. Create Pinpoint Project
    pinpoint = boto3.client('pinpoint', region_name='us-east-1')
    try:
        response = pinpoint.create_app(
            CreateApplicationRequest={'Name': 'SignalWorks'}
        )
        app_id = response['ApplicationResponse']['Id']
        print(f"✅ Pinpoint Project Created. ID: {app_id}")
        print(f"👉 COPY THIS ID TO constants.py: PINPOINT_APP_ID = '{app_id}'")
    except Exception as e:
        print(f"❌ Pinpoint setup failed: {str(e)}")

if __name__ == "__main__":
    setup_cloud()
