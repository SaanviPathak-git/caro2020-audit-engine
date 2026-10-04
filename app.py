"""
CARO 2020 Statutory Audit Engine - Root Entrypoint
Allows running: `streamlit run app.py` directly from project root.
"""

import sys
from pathlib import Path

# Add src to Python path
root_dir = Path(__file__).resolve().parent
src_dir = root_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Import and execute main Streamlit application
from app import *
