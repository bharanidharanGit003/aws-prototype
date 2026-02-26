import json
import os
import boto3
import logging
from datetime import datetime
from shared.constants import BEDROCK_MODEL_ID, DATA_LAKE_BUCKET

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1') # Bedrock is often in us-east-1
s3 = boto3.client('s3')

def generate_insights(city_data):
    """
    Calls Amazon Bedrock (Claude 3) to analyze data and generate vendor insights.
    """
    prompt = f"""
    Human: You are SignalWorks AI, an expert at predicting street vendor demand in India.
    Analyze the following data for {city_data['city']} and provide "Golden Hour" insights.
    
    Data:
    - Weather: {json.dumps(city_data.get('weather'))}
    - Traffic: {json.dumps(city_data.get('traffic'))}
    - Events: {json.dumps(city_data.get('events'))}
    - Mandi Prices: {json.dumps(city_data.get('mandi_prices'))}
    
    Task:
    1. Identify high-demand locations (e.g., specific stadium gates, metro stations, markets).
    2. Suggest the best products to sell.
    3. Suggest a "Fair Sale Price" for common commodities based on the Mandi modal prices (add a 20-30% retail margin).
    4. Provide a 1-sentence summary for the vendor.

    Format the response as a JSON object with keys: "location", "recommended_product", "fair_price_advice", "golden_hour", "summary".
    
    Assistant:
    """

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 500,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })

    try:
        if os.environ.get('AWS_EXECUTION_ENV'):
            response = bedrock.invoke_model(
                modelId=BEDROCK_MODEL_ID,
                body=body
            )
            response_body = json.loads(response.get('body').read())
            raw_text = response_body['content'][0]['text']
            
            # Robust JSON extraction
            try:
                # Find the first '{' and last '}'
                start = raw_text.find('{')
                end = raw_text.rfind('}') + 1
                return json.loads(raw_text[start:end])
            except:
                logger.error(f"Failed to parse AI JSON: {raw_text}")
                return None
        else:
            # Mocking Bedrock for local development
            logger.info("Local test: Mocking Bedrock response")
            return {
                "location": city_data['events'][0]['location'] if city_data['events'] else "Central Market",
                "recommended_product": "Hot Tea and Vada Pav" if city_data['weather'].get('rain_probability', 0) > 0.1 else "Sugar Cane Juice",
                "fair_price_advice": "Sell Onions at ₹35/kg (Mandi: ₹25)",
                "golden_hour": "17:30 - 20:00",
                "summary": f"Match at Wankhede! Reach Gate 4 by 5 PM for high tea demand."
            }
    except Exception as e:
        logger.error(f"Error calling Bedrock: {str(e)}")
        return None

def lambda_handler(event, context):
    """
    Analyze Phase Lambda.
    Triggered after Ingest phase or at 5:30 AM.
    """
    try:
        # 1. Get ingested data
        # In a real pipeline, 'event' would contain the S3 path from the Ingest phase
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        if os.environ.get('AWS_EXECUTION_ENV'):
            # Fetch from S3
            ingest_key = f"ingest/raw/{date_str}/daily_ingest.json"
            predict_key = f"predict/forecasts/{date_str}/price_predictions.json"
            
            ingest_obj = s3.get_object(Bucket=DATA_LAKE_BUCKET, Key=ingest_key)
            predict_obj = s3.get_object(Bucket=DATA_LAKE_BUCKET, Key=predict_key)
            
            ingested_data = json.loads(ingest_obj['Body'].read())
            prediction_data = json.loads(predict_obj['Body'].read())
        else:
            # Load local mock ingest and predict data
            ingest_path = f"data/lake/daily_ingest_{date_str}.json"
            predict_path = f"data/lake/price_predictions_{date_str}.json"
            
            if not os.path.exists(ingest_path) or not os.path.exists(predict_path):
                return {"statusCode": 404, "body": "Input data (ingest or predict) not found"}
            
            with open(ingest_path, 'r') as f:
                ingested_data = json.load(f)
            with open(predict_path, 'r') as f:
                prediction_data = json.load(f)

        # Create a map for predictions by city
        city_predictions = {p['city']: p for p in prediction_data['predictions']}

        # 2. Process each city
        all_insights = []
        for city_item in ingested_data['data']:
            city = city_item['city']
            city_item['ml_predictions'] = city_predictions.get(city)
            
            insight = generate_insights(city_item)
            if insight:
                insight['city'] = city
                all_insights.append(insight)

        # 3. Save Insights
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "insights": all_insights
        }
        
        output_key = f"analyze/processed/{date_str}/vendor_insights.json"
        
        if os.environ.get('AWS_EXECUTION_ENV'):
            s3.put_object(
                Bucket=DATA_LAKE_BUCKET,
                Key=output_key,
                Body=json.dumps(output_data),
                ContentType='application/json'
            )
        else:
            local_out_path = f"data/lake/vendor_insights_{date_str}.json"
            with open(local_out_path, 'w') as f:
                json.dump(output_data, f, indent=4)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Analyze phase completed successfully",
                "insights_count": len(all_insights)
            })
        }

    except Exception as e:
        logger.error(f"Error in Analyze phase: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
