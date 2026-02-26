from functions.feedback.handler import lambda_handler
import json
import os

if __name__ == "__main__":
    print("🚀 Simulating Vendor Feedback (Zero-UI Loop)...")
    
    # Simulate Bharani at Kelambakkam Market sending a "Sold Out" message
    event = {
        "vendor_id": "V001",
        "city": "Chennai",
        "location": "Kelambakkam Market",
        "sales_status": "SOLD_OUT"
    }
    
    response = lambda_handler(event, None)
    
    print(f"Status: {response['statusCode']}")
    print(f"Server Response: {json.loads(response['body'])}")
    
    # Let's check the heatmap file
    heatmap_path = "data/lake/heatmap_chennai.json"
    if os.path.exists(heatmap_path):
        print("\n📈 Current Demand Heatmap (Chennai):")
        with open(heatmap_path, 'r') as f:
            print(json.dumps(json.load(f), indent=4))
