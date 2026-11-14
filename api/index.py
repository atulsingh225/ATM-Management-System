import os
import sys

# Ensure root directory is in sys.path so app and its packages can be imported
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import app

# Vercel Serverless Function looks for the WSGI application object 'app'
# This is explicitly exported for Vercel's Python runtime
