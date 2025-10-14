@echo off
REM build.bat - Build TraderAgent Docker image for Windows

echo 🏗️ Building TraderAgent Docker image...

REM Get version from git tag or use 'latest'
for /f "tokens=*" %%i in ('git describe --tags --always 2^>nul') do set VERSION=%%i
if "%VERSION%"=="" set VERSION=latest

REM Build the image
docker build -t traderagent:%VERSION% -t traderagent:latest .

if %ERRORLEVEL% EQU 0 (
    echo ✅ Successfully built traderagent:%VERSION%
    echo.
    echo Available commands:
    echo   Paper trading:  docker run -d --name trader-paper -e OPENAI_API_KEY=%OPENAI_API_KEY% traderagent:latest
    echo   Development:    docker-compose --profile dev up traderagent-dev
    echo   Live trading:   docker-compose --profile live up traderagent-live
    echo.
    echo 💡 Don't forget to set your OPENAI_API_KEY environment variable!
) else (
    echo ❌ Build failed!
    exit /b 1
)