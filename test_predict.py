from functions.predict.handler import lambda_handler
import json

if __name__ == "__main__":
    print("Running local test for Predict Lambda (SageMaker Logic)...")
    
    # Mock context/event
    event = {}
    context = None
    
    response = lambda_handler(event, context)
    
    print(f"Status: {response['statusCode']}")
    print(f"Body: {json.loads(response['body'])}")
    print("\nCheck 'data/lake/' directory for 'price_predictions_*.json'.")
