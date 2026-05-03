"""Outlay – App factory and initialization."""

from flask import Flask

app = Flask(__name__)

# Import routes at the bottom to avoid circular dependencies.
from app import routes  # noqa: F401, E402
