import sys
import os
from run import app as application  # Hier importierst du die Flask-App

# Füge den aktuellen Pfad hinzu, falls nicht im PYTHONPATH
sys.path.insert(0, os.path.dirname(__file__))

# Setze Umgebungsvariablen falls erforderlich
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_APP'] = 'run.py'
