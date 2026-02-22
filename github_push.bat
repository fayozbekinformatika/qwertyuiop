@echo off
set PATH=C:\Program Files\Git\bin;%PATH%
cd /d e:\merenhub_project
git add .
git commit -m "Learning section - Backend/Frontend categories"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/merenhub.git
git push -u origin main
pause
