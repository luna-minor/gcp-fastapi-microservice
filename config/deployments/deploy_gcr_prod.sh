#!/usr/bin/env bash

# Exit when any command fails
set -e

TIMESTAMP=$(date +"%Y%m%d%H%M")
VERSION="$TIMESTAMP"

# Loop through passed arguments and process them
# https://pretzelhands.com/posts/command-line-flags
for arg in "$@"
do
  case $arg in
    --service_name)
    SERVICE_NAME="${arg#*=}"
    ;;
    --version=*)
    VERSION="${arg#*=}"
    ;;
  esac
done

echo "Deploying ${SERVICE_NAME} - PROD Version ${VERSION}"

# Docs: https://cloud.google.com/sdk/gcloud/reference/run/deploy
gcloud run deploy $SERVICE_NAME \
  --source=. \
  --service-account=$SERVICE_ACCOUNT_EMAIL \
  --platform=managed \
  --region=$GCP_REGION \
  --concurrency=2 \
  --cpu=1 \
  --memory=1Gi \
  --timeout=3600 \
  --max-instances=10 \
  --no-allow-unauthenticated \
  --project=$GCP_PROJECT \
  --update-labels=service-name=$SERVICE_NAME,service-instance=$SERVICE_INSTANCE \
  --tag=$VERSION

# Send traffic to version
gcloud run services update-traffic $SERVICE_NAME \
  --to-latest \
  --platform=managed \
  --region=$GCP_REGION \
  --project=$GCP_PROJECT