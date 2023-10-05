#!/usr/bin/env bash

# `set -e` to exit when any command fails, `set -o nounset` to fail if any variable/flag is empty
set -e
set -o nounset


# Variables
TIMESTAMP=$(date +"%Y%m%d%H%M")
VERSION="d-$TIMESTAMP"
TRAFFIC_PERCENT=0
NO_TRAFFIC_FLAG="--no-traffic"

# Flags, loop through passed arguments and process them
# https://pretzelhands.com/posts/command-line-flags
for arg in "$@"
do
  case $arg in
    --service-config=*)
    SERVICE_CONFIG="${arg#*=}"
    shift
    ;;
    --version=*)
    VERSION="${arg#*=}"
    shift
    ;;
    --traffic-percent=*)
    TRAFFIC_PERCENT="${arg#*=}"
    shift
    ;;
  esac
done

# Load in service config env to reference variables there
source ${SERVICE_CONFIG}

# Check if Service exists, if first time deploying must send 100% of traffic (exclude --no-traffic flag)
SERVICE_EXISTS=$(gcloud run services describe $SERVICE_NAME --platform=managed --project=${DEFAULT_GCP_PROJECT} --region=${DEFAULT_GCP_REGION} --verbosity=critical --no-user-output-enabled && echo 1|| echo 0)

if [ $((SERVICE_EXISTS)) -eq 0 ]; then
   echo "${SERVICE_NAME} does not yet exist in ${DEFAULT_GCP_PROJECT}-${DEFAULT_GCP_REGION} - deploying for first time with 100% of traffic.";
   NO_TRAFFIC_FLAG=""
fi

AUTH_SETTINGS_FLAG="--no-allow-unauthenticated"
if [ $((gcr_allow_unauthenticated)) -eq 1 ]; then
  AUTH_SETTINGS_FLAG="--allow-unauthenticated"
fi

# Deploy Service!
echo "Deploying ${SERVICE_NAME} to Cloud Run: ${DEFAULT_GCP_PROJECT}.${DEFAULT_GCP_REGION}; env=${SERVICE_ENV}; version=${VERSION}; traffic_percent=${TRAFFIC_PERCENT}"

# Docs: https://cloud.google.com/sdk/gcloud/reference/run/deploy
gcloud run deploy ${SERVICE_NAME} \
  --source=. \
  --platform=managed \
  --project=${DEFAULT_GCP_PROJECT} \
  --region=${DEFAULT_GCP_REGION} \
  --service-account=${DEFAULT_SERVICE_ACCOUNT_EMAIL} \
  --concurrency=${gcr_concurrency} \
  --cpu=${gcr_cpu} \
  --memory=${gcr_memory} \
  --timeout=${gcr_timeout} \
  --max-instances=${gcr_max_instances} \
  ${AUTH_SETTINGS_FLAG} \
  --set-env-vars=SERVICE_CONFIG_FILE=${SERVICE_CONFIG} \
  --update-labels=service-name=${SERVICE_NAME},service-env=${SERVICE_ENV} \
  --tag=${VERSION} \
  --revision-suffix=${VERSION} \
  ${NO_TRAFFIC_FLAG}


# Send traffic if flag specified and service already exists (new services are deployed with 100% traffic and skip this step)
if [ $((TRAFFIC_PERCENT)) -gt 0 ] && [ $((SERVICE_EXISTS)) -eq 1 ]; then
  # Revision IDs follow format of SERVICE_NAME-REVISION_SUFFIX
  REVISION_ID=${SERVICE_NAME}-${VERSION}
  
  echo "Sending ${TRAFFIC_PERCENT}% of traffic to revision ID ${REVISION_ID}";
  
  # https://cloud.google.com/sdk/gcloud/reference/run/services/update-traffic#--to-revisions
  gcloud run services update-traffic ${SERVICE_NAME} \
    --platform=managed \
    --region=${DEFAULT_GCP_REGION} \
    --project=${DEFAULT_GCP_PROJECT} \
    --to-revisions=${REVISION_ID}=${TRAFFIC_PERCENT}

fi
