@echo off
setlocal
cd /d "%~dp0"
python -m streamlit run app.py --server.headless false --browser.gatherUsageStats false
endlocal
pause

