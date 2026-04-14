@echo off
cd /d C:\Users\sachi\Downloads\Hardscope\hardscope-assessment

echo Removing helper files...
git rm --cached git_status.txt push_to_github.bat 2>nul
del git_status.txt 2>nul
del push_to_github.bat 2>nul

echo Staging changes...
git add README.md
git add outputs\VALORANT_Creator_QBR_Dashboard.xlsx

echo Committing...
git commit -m "Clean up repo: fix README, update dashboard numbers, remove helper files"

echo Pulling latest...
git pull --rebase origin main

echo Pushing to GitHub...
git push origin main

echo.
echo Done. Check github.com/sachinjain2000/hardscope-assessment
pause
