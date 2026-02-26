# SignalWorks Constants & Configuration

CITIES = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Kolkata"]

import os

# API Keys (Loaded from environment variables for security)
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "YOUR_KEY_HERE")
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "YOUR_KEY_HERE")

# AWS Config
DATA_LAKE_BUCKET = "signalworks-data-lake"
BEDROCK_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"
PINPOINT_APP_ID = "signalworks-pinpoint-app"

# Languages
SUPPORTED_LANGUAGES = {
    "Hindi": "hi",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "English": "en"
}

# Mandi Data (Agmarknet)
AGMARKNET_URL = "https://agmarknet.gov.in/SearchReports/SearchReport.aspx?Report_Name=DailyReportCust&State_Code=MH&District_Code=0&Market_Code=0&Arrival_Date={date}&Arrival_Date_To={date}&Commodity_Code=0"
