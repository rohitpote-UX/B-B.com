"""
Brand Battle — Root WSGI Shim
"""
import os
import sys

backend_dir = os.path.abspath("backend")
if os.path.exists(backend_dir):
    os.chdir(backend_dir)
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

port = os.environ.get("PORT", "8000")
os.execvp("uvicorn", ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(port)])
