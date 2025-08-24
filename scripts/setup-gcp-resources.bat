@echo off
REM Google Cloud Setup Script for AppForge Demo Expense Tracker
REM Run this script to create all required GCP resources

echo Setting up Google Cloud resources for AppForge Demo...

REM Set project variables
set PROJECT_ID=appforge-demo-expense-tracker
set REGION=us-central1
set SERVICE_NAME=expense-tracker-api
set BUCKET_NAME=%PROJECT_ID%-storage

echo.
echo Creating new GCP project...
gcloud projects create %PROJECT_ID% --name="AppForge Demo Expense Tracker"

echo.
echo Setting project as default...
gcloud config set project %PROJECT_ID%

echo.
echo Linking billing account (you'll need to do this manually in console)...
echo Please visit: https://console.cloud.google.com/billing/linkedaccount?project=%PROJECT_ID%
pause

echo.
echo Enabling required APIs...
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable artifactregistry.googleapis.com

echo.
echo Creating Artifact Registry repository...
gcloud artifacts repositories create expense-tracker-repo ^
    --repository-format=docker ^
    --location=%REGION% ^
    --description="Docker repository for expense tracker microservice"

echo.
echo Creating Cloud Storage bucket for SQLite persistence...
gcloud storage buckets create gs://%BUCKET_NAME% ^
    --location=%REGION% ^
    --uniform-bucket-level-access

echo.
echo Setting up IAM permissions for Cloud Run service...
gcloud projects add-iam-policy-binding %PROJECT_ID% ^
    --member="serviceAccount:%PROJECT_ID%@appspot.gserviceaccount.com" ^
    --role="roles/storage.objectAdmin"

echo.
echo Creating Cloud Run service configuration...
echo This will be deployed later with the application code.

echo.
echo Setup complete! Next steps:
echo 1. Link billing account in GCP Console
echo 2. Build and deploy your Flask application
echo 3. Configure domain mapping if needed
echo.
echo Project ID: %PROJECT_ID%
echo Region: %REGION%
echo Artifact Registry: %REGION%-docker.pkg.dev/%PROJECT_ID%/expense-tracker-repo
echo Storage Bucket: gs://%BUCKET_NAME%

pause