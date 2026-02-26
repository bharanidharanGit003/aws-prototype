import json
import os
import boto3
import logging
from datetime import datetime
from shared.constants import DATA_LAKE_BUCKET

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# SageMaker runtime client
sagemaker = boto3.client('sagemaker-runtime', region_name='us-east-1')
s3 = boto3.client('s3')

ENDPOINT_NAME = os.environ.get('SAGEMAKER_ENDPOINT', 'signalworks-price-predictor')

def get_fair_price_prediction(commodity, mandi_price, weather_score, traffic_score):
    """
    Predicts today's fair retail price and forecasts tomorrow's mandi price trend.
    """
    mandi_price = float(mandi_price)
    
    # 1. Today's Fair Retail Price Calculation
    base_margin = 1.25 # 25% profit
    weather_multiplier = 1 + (weather_score * 0.15)
    traffic_multiplier = 1 + (traffic_score * 0.08)
    today_fair_price = (mandi_price / 100) * base_margin * weather_multiplier * traffic_multiplier
    
    # 2. Tomorrow's Mandi Forecast (ML Logic)
    # In a real DeepAR model, this would use historical data. 
    # Here we simulate the trend based on weather/seasonality.
    # If rain is coming tomorrow (weather_score > 0.5), price likely goes up.
    trend = 1.0
    if weather_score > 0.4:
        trend = 1.12 # 12% increase expected due to supply disruption
    elif weather_score < 0.1:
        trend = 0.95 # 5% decrease expected (oversupply)
        
    tomorrow_mandi_forecast = mandi_price * trend
    
    return {
        "today_retail_price": round(today_fair_price, 2),
        "tomorrow_mandi_forecast": round(tomorrow_mandi_forecast, 2),
        "trend": "UP 📈" if trend > 1 else "DOWN 📉" if trend < 1 else "STABLE ➖"
    }

def lambda_handler(event, context):
    """
    Predict Phase Lambda.
    Calculates Fair Price for all ingested data.
    """
    try:
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        # 1. Load Ingested Data
        if os.environ.get('AWS_EXECUTION_ENV'):
            file_key = f"ingest/raw/{date_str}/daily_ingest.json"
            obj = s3.get_object(Bucket=DATA_LAKE_BUCKET, Key=file_key)
            ingested_data = json.loads(obj['Body'].read())
        else:
            local_path = f"data/lake/daily_ingest_{date_str}.json"
            with open(local_path, 'r') as f:
                ingested_data = json.load(f)

        # 2. Process predictions for each city/commodity
        predictions = []
        for city_item in ingested_data['data']:
            city = city_item['city']
            weather_score = city_item['weather'].get('rain_probability', 0)
            traffic_score = city_item['traffic'].get('congestion_index', 0)
            
            city_preds = {"city": city, "commodities": []}
            
            for item in city_item.get('mandi_prices', []):
                price = item.get('modal_price', '2000')
                prediction = get_fair_price_prediction(
                    item['commodity'], 
                    price, 
                    weather_score, 
                    traffic_score
                )
                
                city_preds["commodities"].append({
                    "name": item['commodity'],
                    "mandi_price_today": price,
                    "mandi_forecast_tomorrow": prediction["tomorrow_mandi_forecast"],
                    "trend": prediction["trend"],
                    "fair_retail_price_today": prediction["today_retail_price"],
                    "currency": "INR"
                })
            
            predictions.append(city_preds)

        # 3. Save Predictions
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "predictions": predictions
        }
        
        output_key = f"predict/forecasts/{date_str}/price_predictions.json"
        
        if os.environ.get('AWS_EXECUTION_ENV'):
            s3.put_object(
                Bucket=DATA_LAKE_BUCKET,
                Key=output_key,
                Body=json.dumps(output_data),
                ContentType='application/json'
            )
        else:
            local_out_path = f"data/lake/price_predictions_{date_str}.json"
            with open(local_out_path, 'w') as f:
                json.dump(output_data, f, indent=4)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Predict phase completed", "cities_processed": len(predictions)})
        }

    except Exception as e:
        logger.error(f"Error in Predict phase: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
