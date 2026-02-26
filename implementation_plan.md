# SignalWorks Implementation Plan

## 1. Ingest Phase (Current)
- [x] Create directory structure.
- [x] Implement Ingest Lambda (`handler.py`).
- [x] Mock data for Weather, Traffic, and City Events.
- [x] Implement local testing environment.
- [ ] Connect to real APIs (OpenWeatherMap, City Events scrapers).
- [ ] Deploy to AWS (CDK/Terraform).

## 2. Analyze Phase
- [x] Set up directory structure for Analyze Lambda.
- [x] Implement Bedrock integration logic (Claude 3).
- [x] Define correlation prompt for vendor insights.
- [x] Implement local testing with mock AI responses.
- [ ] Connect to actual AWS Bedrock runtime.

## 3. Predict Phase
- [ ] Integrate Amazon SageMaker for "Fair Price" forecasting.
- [ ] Ingest Mandi wholesale rates (scraping from Agmarknet or similar).

## 4. Deliver Phase
- [x] Set up directory structure for Deliver Lambda.
- [x] Implement Amazon Pinpoint SMS delivery logic (Pending 24hr activation).
- [x] Integrate Amazon Translate for multi-language support.

## 5. Scheme Bot (New!)
- [x] Set up Amazon Textract integration for OCR.
- [x] Implement Doc-to-Advice logic with Claude 3 Haiku.
- [ ] Create S3 trigger for automatic document processing.

## 6. Feedback Phase
- [ ] DynamoDB schema for vendor location updates.
- [ ] Demand heatmap update logic.
