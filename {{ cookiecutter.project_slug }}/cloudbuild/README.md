# CI/CD with Cloud Build

Continuous Integration (CI) and Continuous Delivery (CD) automates the process of building, testing, and deployment of a service or application. 
It automates the process of moving code from your local machine, to a git repository, and finally to the deployment target (GCP for ex.).
CI/CD flows can be used to ensure code updates are linted, tested, reach a coverage threshold, etc. - before being deployed to a production instance.

[Cloud Build](https://cloud.google.com/build/docs/overview) is a service that executes your builds on Google Cloud Platform's infrastructure.
Cloud Build executes your build as a series of build steps, where each build step is run in a Docker container.
Cloud Build executes a set of build steps defined in a yaml or json file and can be triggered manually via API, schedule, PubSub, or through triggers such as a Push to a specific branch in a git repo or opening of a Pull Request.

This chassis comes with a default `cloudbuild` directory with everything needed to setup a CI/CD flow with Cloud Build and GitHub build triggers.
This README walks through setting it up along with the details of the files and assumptions made.
Will setup push-to-main branch and pr-to-main branch build triggers that will execute a build using a standard cloudbuild.yaml with steps for validating code formatting, running tests, and deploying with a certain traffic percentage based on the trigger (Pull Request to main/master or Push to main/master).
The default Cloud Build steps utilizes many of the same commands defined in the chassis's CLI and uses the same deployment scripts, to ensure testing and deployment are done in the same way whether running locally or in Cloud Build.


### Contents
- [Docs/Resources](#docs--resources)
- [Usage](#usage)
- [Folder Contents](#folder-contents)


### Docs / Resources
- [Cloud Build docs](https://cloud.google.com/build/docs/overview)
- [Building and debugging locally](https://cloud.google.com/build/docs/build-debug-locally)
- [Triggering from GitHub](https://cloud.google.com/build/docs/automating-builds/build-repos-from-github)


### Usage
Sets up GitHub build triggers to run a build in Cloud Build configured via a default cloudbuild.yaml file.
Executes code format checks, runs tests, and if passing all steps deploys the service.
Pushes to master/main will run the `deploy_prod.sh` script deploying to "production" (ie. if Cloud Run or App Engine - 100% traffic version, etc.)
Pull Requests targeting master/main will run the `deploy_dev.sh` script deploying to "development" (ie. if Cloud Run or App Engine - no traffic versions, etc.)

- Optionally review [cloudbuild.yaml](./cloudbuild.yaml) - the main Cloud Build file, showing what build steps are used by default.
    - Includes automated testing, code format tests, and a deploy prod/dev step.
    - Can comment out or add/edit certain steps to meet needs of a given service.
- Optionally review [pr_main_trigger.yaml](./pr_main_trigger.yaml) and/or [push_main_trigger.yaml](./pr_main_trigger.yaml) which have the configuration for the GitHub build triggers, or add more as needed.
- From root:
    - `bash ./cloudbuild/create_update_prod_build_trigger.sh` - Setup prod build trigger (ran on Pushes to main/master branch)
    - `bash ./cloudbuild/create_update_dev_build_trigger.sh` - Setup dev build trigger (ran on Pull Requests targeting main/master branch)
- NOTE:
    - The steps run as the Cloud Build Service Account for whatever GCP Project the build is running in.
    - You can grant the Cloud Build Service Account permission to impersonate another (or all) Service Accounts to allow it to run integration tests and act as a specific Service Account (this is done by default in tech-managed Projects).

### Folder Contents
Description of all files in this directory.

- [cloudbuild.yaml](./cloudbuild.yaml) - the main Cloud Build file with the specified default build steps.
    - Includes automated testing, code format tests, and a deploy prod/dev step.
    - Can comment out or add/edit certain steps to meet needs of a given service.
    - Makes use of many of the same scripts in scripts directory (`run_tests.sh`, `deploy_prod.sh` when on master (or main) branch, and `deploy_dev.sh` on others).
- [local_build.sh](./local_build.sh) - run Cloud Build locally, asks to do a dry run (validate syntax only) or a full run (will execute all steps on local machine).
    - requires `cloud-build-local` gcloud component (see docs link above for details).
    - NOTE: if doing a full run it will execute all steps, including any deployment steps.
    - NOTE (v0.5.2): cloud-build-local does not ignore the contents of .gcloudignore, meaning also files defined in .gcloudignore will be deployed (see [here](https://github.com/GoogleCloudPlatform/cloud-build-local/issues/84)). 
- [submit_build.sh](./submit_build.sh) - manually trigger a build.
    - NOTE: this will manually trigger a full build in Cloud Build, including any deployment steps.
- [prod_build_trigger.yaml](./prod_build_trigger.yaml) - a yaml configuration of the 'prod' trigger that will trigger a build and deployment to 'prod'.
    - Specifies certain files to ignore, meaning changes made to certain files or in certain folders won't trigger a build.
- [create_update_prod_build_trigger.sh](./create_update_prod_build_trigger.sh) - create/updates GitHub Build trigger on pushes to master (or main).
    - Setup to trigger on Pushes to "master" or "main" branch.
    - NOTE: if you edit the prod_build_trigger.yaml trigger configuration you need to manually re-run this script to update the trigger.
- [dev_build_trigger.yaml](./dev_build_trigger.yaml) - a yaml configuration of the 'dev' trigger that will trigger a build and deployment to 'dev'.
    - Specifies certain files to ignore, meaning changes made to certain files or in certain folders won't trigger a build.
- [create_update_dev_build_trigger.sh](./create_update_dev_build_trigger.sh) - create/updates GitHub Build trigger on Pull Request to master (or main).
    - Setup to trigger on Pull Requests targeting "master" or "main" branch.
    - NOTE: if you edit the dev_build_trigger.yaml trigger configuration you need to manually re-run this script to update the trigger.
