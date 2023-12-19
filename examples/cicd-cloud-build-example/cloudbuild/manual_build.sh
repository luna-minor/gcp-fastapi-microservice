#!/usr/bin/env bash


# `set -e` to exit when any command fails, `set -o nounset` to fail if any variable/flag is empty
set -e
set -o nounset


# Flags, loop through passed arguments and process them
# https://pretzelhands.com/posts/command-line-flags
for arg in "$@"
do
  case $arg in
    --project-id=*)
    PROJECT_ID="${arg#*=}"
    shift
    ;;
  esac
done


# Submit build job to Cloud Build
# https://cloud.google.com/sdk/gcloud/reference/builds/submit
gcloud builds submit .\
  --config ./cloudbuild/cloudbuild.yaml \
  --project ${PROJECT_ID} \
  --substitutions BRANCH_NAME=$(git branch --show-current),SHORT_SHA="manual-build"
