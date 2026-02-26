from functions.analyze.handler import lambda_handler
import json

if __name__ == "__main__":
    print("Running local test for Analyze Lambda...")
    
    # Mock context/event
    event = {}
    context = None
    
    response = lambda_handler(event, context)
    
    print(f"Status: {response['statusCode']}")
    print(f"Body: {json.loads(response['body'])}")
    print("\nCheck 'data/lake/' directory for the 'vendor_insights_*.json' output.")
