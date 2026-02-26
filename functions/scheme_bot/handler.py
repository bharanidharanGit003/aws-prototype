import json
import os
import boto3
import logging
from shared.constants import BEDROCK_MODEL_ID, DATA_LAKE_BUCKET

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

textract = boto3.client('textract', region_name='us-east-1')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
s3 = boto3.client('s3')

def extract_text_from_s3(bucket, key):
    """
    Uses Amazon Textract to extract text from an image/PDF in S3.
    """
    logger.info(f"Extracting text from s3://{bucket}/{key}")
    try:
        response = textract.detect_document_text(
            Document={'S3Object': {'Bucket': bucket, 'Name': key}}
        )
        
        extracted_text = ""
        for item in response['Blocks']:
            if item['BlockType'] == 'LINE':
                extracted_text += item['Text'] + " "
        
        return extracted_text
    except Exception as e:
        logger.error(f"Textract failed: {str(e)}")
        return None

def analyze_document_with_ai(text, doc_type="PM SVANidhi Application"):
    """
    Uses Bedrock to analyze the extracted text and provide vendor advice.
    """
    prompt = f"""
    Human: You are the SignalWorks Scheme Bot. A vendor has uploaded a {doc_type}.
    Here is the text extracted from their document:
    ---
    {text}
    ---
    
    Task:
    1. Summarize the key details (Name, Application ID, Status).
    2. Identify if any critical information is missing or unclear (e.g., signature, date).
    3. Provide 3 simple steps in Tamil to help them complete the application.
    
    Format your response in a supportive, helpful tone for a street vendor.
    
    Assistant:
    """

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": prompt}]
    })

    try:
        if os.environ.get('AWS_EXECUTION_ENV'):
            response = bedrock.invoke_model(modelId=BEDROCK_MODEL_ID, body=body)
            response_body = json.loads(response.get('body').read())
            return response_body['content'][0]['text']
        else:
            return f"Mock AI Analysis of: {text[:50]}... (Advice: Application looks 80% complete. Please add your signature!)"
    except Exception as e:
        logger.error(f"Bedrock analysis failed: {str(e)}")
        return "I can read your document but I'm having trouble analyzing it right now. Please try again."

def lambda_handler(event, context):
    """
    Scheme Bot Lambda.
    Triggered when a vendor uploads a document image to S3.
    """
    try:
        # In real scenario, event['Records'][0]['s3']['object']['key']
        # For testing, we can pass it in the event
        bucket = event.get('bucket', DATA_LAKE_BUCKET)
        key = event.get('key')
        
        if not key:
            return {"statusCode": 400, "body": "No S3 key provided"}

        # 1. OCR with Textract
        extracted_text = extract_text_from_s3(bucket, key)
        
        if not extracted_text:
            return {"statusCode": 500, "body": "Could not extract text from document"}

        # 2. Reasoning with Bedrock
        advice = analyze_document_with_ai(extracted_text)

        # 3. Output (Normally would send via Pinpoint, here we return it)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Document processed successfully",
                "extracted_text_preview": extracted_text[:100],
                "ai_advice": advice
            }, ensure_ascii=False)
        }

    except Exception as e:
        logger.error(f"Error in Scheme Bot: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
