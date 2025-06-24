@echo off
REM Test the cache refresh scripts to make sure they work

echo Testing MSE Cache Refresh Scripts
echo =================================

cd /d "c:\Users\innow\OneDrive\Desktop\mse_api"

echo.
echo 1. Testing simple daily refresh...
python daily_cache_refresh.py

echo.
echo 2. Testing full refresh script (dry run)...
python refresh_cache.py --symbols AIRTEL,TNM --ranges 1day,1month --dry-run

echo.
echo 3. Testing priority refresh (dry run)...
python refresh_cache.py --priority --dry-run

echo.
echo Testing complete! Check logs for details.
pause
