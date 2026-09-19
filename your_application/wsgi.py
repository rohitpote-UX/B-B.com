"""
Brand Battle — Render WSGI/ASGI Compatibility Shim (Root)
If Render executes 'gunicorn your_application.wsgi' from repository root,
this shim switches to backend directory and starts Uvicorn.
"""
import os
import sys

backend_dir = os.path.abspath("backend")
if os.path.exists(backend_dir):
    os.chdir(backend_dir)
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

port = os.environ.get("PORT", "8000")
print(f"🚀 Launching Brand Battle FastAPI server via Uvicorn on port {port}...")
os.execvp("uvicorn", ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(port)])
