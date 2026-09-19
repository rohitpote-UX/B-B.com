"""
Brand Battle — WSGI Shim
"""
import os
import sys

port = os.environ.get("PORT", "8000")
os.execvp("uvicorn", ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(port)])
