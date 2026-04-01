"""
Entry point for the SANA Flask backend.

Development:
    python run.py

Production (gunicorn):
    gunicorn -w 4 -b 0.0.0.0:5000 "run:app"
"""

import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    port  = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    print(f"\n🚀  SANA API running on http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
