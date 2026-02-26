from functions.ingest.handler import lambda_handler
import json

if __name__ == "__main__":
    print("Running local test for Ingest Lambda...")
    
    # Mock context/event
    event = {}
    context = None
    
    response = lambda_handler(event, context)
    
    print(f"Status: {response['statusCode']}")
    print(f"Body: {json.loads(response['body'])}")
    print("\nCheck 'data/lake/' directory for the output JSON.")
