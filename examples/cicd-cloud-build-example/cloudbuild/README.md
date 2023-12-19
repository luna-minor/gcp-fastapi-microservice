# CI/CD with Cloud Build

Continuous Integration (CI) and Continuous Delivery (CD) automates the process of building, testing, and deployment of a service or application. 
It automates the process of moving code from your local machine, to a git repository, and finally to the deployment target (GCP Cloud Run, or GKE for ex.).
CI/CD flows can be used to ensure code updates are linted, tested, reach a coverage threshold, etc. - before being deployed.

[Cloud Build](https://cloud.google.com/build/docs/overview) is a service that executes your builds on Google Cloud Platform's infrastructure.
Cloud Build executes a set of build steps defined in a yaml or json file, where each build step is run in a Docker container with an image specified by the build config. Builds can be triggered manually via API or gcloud, scheduled, via PubSub, or through triggers such as a git push to a specific branch in a git repo or opening of a pull request.

This chassis comes with a default `cloudbuild` directory with everything needed to setup a CI/CD flow with Cloud Build and GitHub build triggers, including a helper python CLI for creating,updating,deleting the build triggers, as well as triggering manual builds.


## Documentation / Resources
- [Cloud Build docs](https://cloud.google.com/build/docs/overview)
- [Building and debugging locally](https://cloud.google.com/build/docs/build-debug-locally)
- [Triggering from GitHub](https://cloud.google.com/build/docs/automating-builds/build-repos-from-github)


## Usage
This directory comes with a python helper CLI:

- From project root dir, run `python cli/main.py cloudbuild --help` to view full list of commands and options.
- Setup Cloud Build Github Triggers:
    - `python cli/main.py cloudbuild setup`
    - Will prompt for the GCP Project ID to create the triggers in.
- Optionally review [cloudbuild.yaml](./cloudbuild.yaml) - the main Cloud Build file, showing what build steps are used by default.
    - Includes automated testing, code format tests, and a deploy prod/dev step.
    - Can comment out or add/edit certain steps to meet needs of a given service.
- Optionally review [pr_main_trigger.yaml](./pr_main_trigger.yaml) and/or [push_main_trigger.yaml](./pr_main_trigger.yaml) which have the configuration for the GitHub build triggers.
    - Pushes to master/main will trigger [push_main_trigger.yaml](./push_main_trigger.yaml) and deploy to "production" (ie. if Cloud Run or App Engine - 100% traffic version, etc.)
    - Pull Requests targeting master/main will trigger [push_main_trigger.yaml](./push_main_trigger.yaml) and deploy to "development" (ie. if Cloud Run or App Engine - no traffic versions, etc.)
    - The build trigger yaml files can be edited (to ignore certain files for ex.), or the [cloudbuild.yaml](./cloudbuild.yaml) can be edited to add/remove checks or steps, or to deploy to different environments with different settings.
    - NOTE: If updating a build trigger's yaml configuration, you must also update them in GCP, via the below command:
        - `python cli/main.py cloudbuild update-build-trigger`
- NOTE:
    - The steps run as the Cloud Build Service Account for whatever GCP Project the build is running in.
    - You can grant the Cloud Build Service Account permission to impersonate another (or all) Service Accounts to allow it to run integration tests and act as a specific Service Account.


### Folder Contents
Description of key files in this directory.

- [cloudbuild.yaml](./cloudbuild.yaml): the main Cloud Build file with the specified default build steps.
    - Includes automated testing, code format tests, and a deploy prod/dev step.
    - Can comment out or add/edit certain steps to meet needs of a given service.
- [pr_main_trigger.yaml](./pr_main_trigger.yaml): YAML file configuration for a Cloud Build Trigger ran on PRs targeting the main/master branch of a GitHub repo.
    - Specifies certain files to ignore, meaning changes made to certain files or in certain folders won't trigger a build.
- [push_main_trigger.yaml](./push_main_trigger.yaml): YAML file configuration for a Cloud Build Trigger ran on pushes to the main/master branch of a GitHub repo.
    - Specifies certain files to ignore, meaning changes made to certain files or in certain folders won't trigger a build.
- [cloudbuild_cli.py](./cloudbuild_cli.py): Python CLI helper to setup, update, and delete the build triggers
    - From project root dir, can run `python cli/main.py cloudbuild --help` to view full list of commands and options.