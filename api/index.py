import sys
import os

# Add root folder to sys.path so Python can find analytics.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analytics import app
