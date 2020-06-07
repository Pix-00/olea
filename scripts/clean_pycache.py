import shutil
from pathlib import Path

DIR = Path(__file__).parents[1]

for path in DIR.glob('**/__pycache__'):
    shutil.rmtree(path)
