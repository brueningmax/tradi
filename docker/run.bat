@echo off
REM run.bat - Run TraderAgent in different modes for Windows

setlocal enabledelayedexpansion

REM Default values
set MODE=paper
set DETACHED=
set OPENAI_KEY=%OPENAI_API_KEY%

:parse_args
if "%~1"=="" goto validate
if "%~1"=="-m" (
    set MODE=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--mode" (
    set MODE=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="-d" (
    set DETACHED=-d
    shift
    goto parse_args
)
if "%~1"=="--detached" (
    set DETACHED=-d
    shift
    goto parse_args
)
if "%~1"=="-k" (
    set OPENAI_KEY=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--key" (
    set OPENAI_KEY=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="-h" goto show_help
if "%~1"=="--help" goto show_help

echo Unknown option: %~1
goto show_help

:show_help
echo 🤖 TraderAgent Docker Runner
echo.
echo Usage: %0 [OPTIONS]
echo.
echo Options:
echo   -m, --mode MODE     Trading mode: paper, live, dev (default: paper)
echo   -d, --detached      Run in detached mode (background)
echo   -k, --key KEY       OpenAI API key (or set OPENAI_API_KEY env var)
echo   -h, --help          Show this help message
echo.
echo Examples:
echo   %0                                    # Paper trading (interactive)
echo   %0 -m paper -d                       # Paper trading (background)
echo   %0 -m dev                            # Development mode
echo   %0 -m live -k sk-xxx...              # Live trading with API key
echo.
echo ⚠️ WARNING: Live mode uses real money! Use with extreme caution.
goto end

:validate
REM Validate OpenAI API key
if "%OPENAI_KEY%"=="" (
    echo ❌ Error: OpenAI API key is required!
    echo    Set OPENAI_API_KEY environment variable or use -k option
    exit /b 1
)

REM Execute based on mode
if "%MODE%"=="paper" goto paper_mode
if "%MODE%"=="live" goto live_mode
if "%MODE%"=="dev" goto dev_mode

echo ❌ Error: Invalid mode '%MODE%'. Valid modes: paper, live, dev
exit /b 1

:paper_mode
echo 📊 Starting TraderAgent in PAPER TRADING mode...
docker run %DETACHED% --rm --name trader-paper -e OPENAI_API_KEY=%OPENAI_KEY% -v "%cd%\data:/app/data" traderagent:latest python main.py --live --paper
goto end

:live_mode
echo ⚠️ Starting TraderAgent in LIVE TRADING mode...
echo ⚠️ THIS WILL USE REAL MONEY!
echo.
set /p confirm="Are you sure? Type 'YES' to continue: "
if not "%confirm%"=="YES" (
    echo Cancelled.
    goto end
)
docker run %DETACHED% --rm --name trader-live -e OPENAI_API_KEY=%OPENAI_KEY% -v "%cd%\data:/app/data" traderagent:latest python main.py --live
goto end

:dev_mode
echo 🛠️ Starting TraderAgent in DEVELOPMENT mode...
docker-compose --profile dev up traderagent-dev
goto end

:end