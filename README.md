# SignalWorks - AWS AI for Bharat Hackathon

SignalWorks is a serverless, AI-powered "Zero-UI" solution designed to empower Indian street vendors with "Morning Intelligence".

## Project Goals
- **Zero-UI**: Accessibility via SMS and IVR for vendors with 2G/basic phones.
- **Morning Intelligence**: Deliver insights on location, demand, and fair price before 6:00 AM.
- **Scalability**: 100% serverless AWS architecture.

## Tech Stack
- **AI**: Amazon Bedrock (Claude 3), Amazon SageMaker.
- **Communication**: Amazon Pinpoint, Amazon Connect, Amazon Polly.
- **Backend**: AWS Lambda (Python), Amazon DynamoDB.
- **Orchestration**: AWS Step Functions, Amazon EventBridge.
- **Storage**: Amazon S3 (Data Lake).

## Repository Structure
- `functions/`: AWS Lambda functions for different workflow phases.
  - `ingest/`: Daily data ingestion (Weather, Traffic, Events).
- `shared/`: Common utilities and constants.
- `infra/`: (TBD) Infrastructure as Code (CDK/Terraform).
- `data/lake/`: Local mock data lake for testing.

## Getting Started
### Local Testing
To test the Ingest phase locally:
```bash
pip install -r functions/ingest/requirements.txt
python3 test_ingest.py
```
This will generate a JSON file in `data/lake/` containing the ingested data.

## Next Steps
1. Implement the **Analyze** phase using Amazon Bedrock.
2. Integrate real Mandi price data for the **Predict** phase.
3. Configure the Step Functions state machine to orchestrate the workflow.
