@echo off
REM MSE Daily Cache Refresh - Windows Task Scheduler
REM Run this batch file daily via Windows Task Scheduler

echo MSE Daily Cache Refresh - %date% %time%
cd /d "c:\Users\innow\OneDrive\Desktop\mse_api"

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Run the daily refresh script
echo Starting cache refresh...
python daily_cache_refresh.py

REM Check exit code
if %ERRORLEVEL% EQU 0 (
    echo Cache refresh completed successfully!
) else (
    echo Cache refresh failed with errors!
)

echo Refresh completed at %date% %time%
REM Uncomment the next line if you want to see output when run manually
REM pause
