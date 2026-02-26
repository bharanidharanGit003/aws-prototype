import json
import os
import boto3
import logging
from datetime import datetime
from shared.constants import DATA_LAKE_BUCKET

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Table names (would be created via CDK/Console)
FEEDBACK_TABLE = "SignalWorks-VendorFeedback"
HEATMAP_TABLE = "SignalWorks-DemandHeatmap"

def update_demand_heatmap(city, location, sales_status):
    """
    Updates the heat density of a specific location based on vendor success.
    sales_status: 'SOLD_OUT', 'MODERATE', 'LOW'
    """
    weight = 5 if sales_status == 'SOLD_OUT' else 2 if sales_status == 'MODERATE' else 0
    
    logger.info(f"Updating heatmap for {location} in {city} with weight {weight}")
    
    try:
        # Only use DynamoDB if we are specifically in a cloud env and table exists
        if os.environ.get('AWS_EXECUTION_ENV') and not os.environ.get('FORCE_LOCAL'):
            table = dynamodb.Table(HEATMAP_TABLE)
            table.update_item(
                Key={'city': city, 'location': location},
                UpdateExpression="ADD demand_density :w, checkin_count :c",
                ExpressionAttributeValues={':w': weight, ':c': 1}
            )
        else:
            # Local saving for testing
            os.makedirs('data/lake', exist_ok=True)
            heatmap_path = f"data/lake/heatmap_{city.lower()}.json"
            data = {}
            if os.path.exists(heatmap_path):
                with open(heatmap_path, 'r') as f:
                    data = json.load(f)
            
            entry = data.get(location, {"demand_density": 0, "checkin_count": 0})
            entry["demand_density"] += weight
            entry["checkin_count"] += 1
            data[location] = entry
            
            with open(heatmap_path, 'w') as f:
                json.dump(data, f, indent=4)
        return True
    except Exception as e:
        logger.error(f"Heatmap update failed: {str(e)}")
        return False

def lambda_handler(event, context):
    """
    Feedback Phase Lambda.
    Handles vendor check-ins and sales reports.
    """
    try:
        # Example event: {"vendor_id": "V001", "city": "Chennai", "location": "Kelambakkam Market", "sales_status": "SOLD_OUT"}
        vendor_id = event.get('vendor_id')
        city = event.get('city')
        location = event.get('location')
        sales_status = event.get('sales_status', 'MODERATE')
        
        timestamp = datetime.now().isoformat()
        
        # 1. Store Feedback for Audit/History
        if os.environ.get('AWS_EXECUTION_ENV'):
            # In real AWS, we'd use dynamodb.Table(FEEDBACK_TABLE).put_item(...)
            pass
        
        # 2. Update the Demand Heatmap (The critical part for tomorrow's AI)
        success = update_demand_heatmap(city, location, sales_status)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Feedback received. Heatmap updated.",
                "vendor_id": vendor_id,
                "impact": "High" if sales_status == 'SOLD_OUT' else "Normal"
            })
        }

    except Exception as e:
        logger.error(f"Error in Feedback phase: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
