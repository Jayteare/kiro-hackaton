@echo off
REM Cloud Run Deployment Script for AppForge Demo
REM Run this after building your Docker image

echo Deploying AppForge Demo to Cloud Run...

REM Set deployment variables
set PROJECT_ID=appforge-demo-expense-tracker
set REGION=us-central1
set SERVICE_NAME=expense-tracker-api
set IMAGE_URL=%REGION%-docker.pkg.dev/%PROJECT_ID%/expense-tracker-repo/expense-tracker:latest
set BUCKET_NAME=%PROJECT_ID%-storage

echo.
echo Building and pushing Docker image...
gcloud builds submit --tag %IMAGE_URL% .

echo.
echo Deploying to Cloud Run...
gcloud run deploy %SERVICE_NAME% ^
    --image=%IMAGE_URL% ^
    --platform=managed ^
    --region=%REGION% ^
    --allow-unauthenticated ^
    --memory=512Mi ^
    --cpu=0.5 ^
    --min-instances=0 ^
    --max-instances=10 ^
    --concurrency=80 ^
    --timeout=60s ^
    --set-env-vars="DATABASE_URL=sqlite:////tmp/expenses.db,STORAGE_BUCKET=%BUCKET_NAME%,FLASK_ENV=production" ^
    --port=8080

echo.
echo Getting service URL...
gcloud run services describe %SERVICE_NAME% --region=%REGION% --format="value(status.url)"

echo.
echo Deployment complete!
echo Your expense tracker API is now live and cost-optimized for Google Cloud.

pause