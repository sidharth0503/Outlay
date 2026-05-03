"""Outlay – Application entry point.

Run this file directly to start the Flask development server:

    python run.py

The server binds to 0.0.0.0:5000 so that it is reachable from outside
the host – a requirement when the app is baked into a Packer image.
"""

from app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
