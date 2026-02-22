@echo off
echo ========================================
echo   MerenHub ni GitHub'ga Yuklash
echo ========================================
echo.

cd /d e:\merenhub_project

echo Fayllarni qoshish...
"C:\Program Files\Git\bin\git.exe" add .

echo Commit yozish...
"C:\Program Files\Git\bin\git.exe" commit -m "Learning section - Backend/Frontend categories"

echo.
echo ========================================
echo   Endi GitHub username va repository nomini kiriting
echo ========================================
echo.

set /p GH_USER="GitHub username: "
set /p GH_REPO="Repository nomi (masalan: merenhub): "

echo.
echo Ulanish va yuklash...
"C:\Program Files\Git\bin\git.exe" branch -M main
"C:\Program Files\Git\bin\git.exe" remote add origin https://github.com/%GH_USER%/%GH_REPO%.git
"C:\Program Files\Git\bin\git.exe" push -u origin main

echo.
echo ==================
echo   TAYYOR!
echo ==================
pause
