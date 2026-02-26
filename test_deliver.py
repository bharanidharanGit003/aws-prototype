from functions.deliver.handler import lambda_handler
import json

if __name__ == "__main__":
    print("Running local test for Deliver Lambda (Golden Hour SMS)...")
    
    # Mock context/event
    event = {}
    context = None
    
    response = lambda_handler(event, context)
    
    print(f"Status: {response['statusCode']}")
    body = json.loads(response['body'])
    print(f"Message: {body['message']}")
    print(f"Total Sent: {body['total_sent']}")
    
    print("\nDetailed Results:")
    for result in body.get('results', []):
        print(f" - Vendor {result['vendor_id']} ({result['city']}): {result['status']}")
