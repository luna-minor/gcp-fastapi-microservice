#!/usr/bin/env bash

# 'e' Exits when any command fails, '0 nounset' exits as error if a variable is unset
set -eo nounset

TIMESTAMP=$(date +"%Y%m%d%H%M")
VERSION="$TIMESTAMP"
TRAFFIC_PERCENT=0

# Loop through passed arguments and process them
# https://pretzelhands.com/posts/command-line-flags
for arg in "$@"
do
  case $arg in
    --gcp_project=*)
    GCP_PROJECT="${arg#*=}"
    shift
    ;;
    --gcp_region=*)
    GCP_REGION="${arg#*=}"
    shift
    ;;
    --service_name=*)
    SERVICE_NAME="${arg#*=}"
    shift
    ;;
    --service_env=*)
    SERVICE_ENV="${arg#*=}"
    shift
    ;;
    --service_account=*)
    SERVICE_ACCOUNT_EMAIL="${arg#*=}"
    shift
    ;;
    --version=*)
    VERSION="${arg#*=}"
    ;;
    --traffic_percent=*)
    TRAFFIC_PERCENT="${arg#*=}"
    shift
    ;;
  esac
done

echo "Deploying ${SERVICE_NAME} to ${GCP_PROJECT}.${GCP_REGION}; env=${SERVICE_ENV}; version=${VERSION}; traffic_percent=${TRAFFIC_PERCENT}"

# Docs: https://cloud.google.com/sdk/gcloud/reference/run/deploy
gcloud run deploy ${SERVICE_NAME} \
  --source=. \
  --service-account=${SERVICE_ACCOUNT_EMAIL} \
  --platform=managed \
  --region=${GCP_REGION} \
  --concurrency=2 \
  --cpu=1 \
  --memory=1Gi \
  --timeout=3600 \
  --max-instances=10 \
  --no-allow-unauthenticated \
  --project=${GCP_PROJECT} \
  --update-labels=service-name=${SERVICE_NAME},service-env=${SERVICE_ENV} \
  --tag=${VERSION} \
  --revision-suffix=${VERSION} \
  --no-traffic


if [ "${TRAFFIC_PERCENT}" -gt "0" ]; then
  # Revision IDs follow format of SERVICE_NAME-REVISION_SUFFIX
  REVISION_ID=${SERVICE_NAME}-${VERSION}
  
  echo "Sending ${TRAFFIC_PERCENT}% of traffic to revision ID ${REVISION_ID}";
  
  # https://cloud.google.com/sdk/gcloud/reference/run/services/update-traffic#--to-revisions
  gcloud run services update-traffic ${SERVICE_NAME} \
    --platform=managed \
    --region=${GCP_REGION} \
    --project=${GCP_PROJECT} \
    --to-revisions=${REVISION_ID}=${TRAFFIC_PERCENT}
fi
