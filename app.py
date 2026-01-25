import os
import sys

# Ensure the root directory is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from guidebook.gradio_app import app

if __name__ == "__main__":
    app.launch()
