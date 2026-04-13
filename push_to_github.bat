@echo off
cd /d C:\Users\sachi\Downloads\Hardscope\hardscope-assessment
echo.
echo === Staging all files ===
git add .
echo.
echo === Committing ===
git commit -m "Add all deliverables + strengthen analysis (tier benchmarks, limitations, PPTX slide 6)"
echo.
echo === Pushing to GitHub ===
git push -u origin main
echo.
echo === Done! Check https://github.com/sachinjain2000/hardscope-assessment ===
pause
