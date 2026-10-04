@echo off
title CARO 2020 Statutory Audit Testing Engine
echo =====================================================================
echo    Launching CARO 2020 Statutory Audit Engine (Streamlit Web App)
echo =====================================================================
echo.
cd /d "%~dp0"
python -m streamlit run app.py
pause
