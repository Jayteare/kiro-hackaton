@echo off
REM Cleanup script to remove GCP resources and avoid charges
REM WARNING: This will delete all project resources!

echo WARNING: This will delete ALL resources in the AppForge Demo project!
echo This action cannot be undone.
echo.
set /p CONFIRM="Type 'DELETE' to confirm: "

if not "%CONFIRM%"=="DELETE" (
    echo Cleanup cancelled.
    pause
    exit /b
)

set PROJECT_ID=appforge-demo-expense-tracker
set REGION=us-central1
set SERVICE_NAME=expense-tracker-api
set BUCKET_NAME=%PROJECT_ID%-storage

echo.
echo Deleting Cloud Run service...
gcloud run services delete %SERVICE_NAME% --region=%REGION% --quiet

echo.
echo Deleting Cloud Storage bucket...
gcloud storage rm -r gs://%BUCKET_NAME% --quiet

echo.
echo Deleting Artifact Registry repository...
gcloud artifacts repositories delete expense-tracker-repo --location=%REGION% --quiet

echo.
echo Deleting entire project (recommended for complete cleanup)...
set /p DELETE_PROJECT="Delete entire project? (y/n): "

if /i "%DELETE_PROJECT%"=="y" (
    gcloud projects delete %PROJECT_ID% --quiet
    echo Project deletion initiated. It may take a few minutes to complete.
) else (
    echo Project kept. Individual resources have been deleted.
)

echo.
echo Cleanup complete!
pause