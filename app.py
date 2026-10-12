"""
Root Entrypoint for Portfolio Streamlit App
Runs the retro pixel-art Utility Bill Decoder dashboard.
"""
import runpy
import sys
import os

# Ensure current working directory is on PYTHONPATH
if os.path.abspath(".") not in sys.path:
    sys.path.insert(0, os.path.abspath("."))

# Run source/demo_app.py in this context
runpy.run_path(os.path.join("source", "demo_app.py"), run_name="__main__")
