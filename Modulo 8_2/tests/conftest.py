"""Hace importables los modulos de src/ desde las pruebas."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # app_gradio.py vive en la raiz del proyecto
