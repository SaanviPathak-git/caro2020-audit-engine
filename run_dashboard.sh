#!/bin/bash
echo "====================================================================="
echo "   Launching CARO 2020 Statutory Audit Engine (Streamlit Web App)"
echo "====================================================================="
cd "$(dirname "$0")"
python3 -m streamlit run app.py
