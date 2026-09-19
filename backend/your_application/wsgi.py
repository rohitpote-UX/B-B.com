"""
Brand Battle — Render WSGI/ASGI Compatibility Shim
If Render executes the default placeholder 'gunicorn your_application.wsgi',
this shim intercepts it and starts the production Uvicorn ASGI server.
"""
import os
import sys

port = os.environ.get("PORT", "8000")
print(f"🚀 Launching Brand Battle FastAPI server via Uvicorn on port {port}...")
os.execvp("uvicorn", ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(port)])
