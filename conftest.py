from pathlib import Path
import os
import sys


ROOT_DIR = Path(__file__).resolve().parent
BACK_DIR = ROOT_DIR / "back"


if str(BACK_DIR) not in sys.path:
    sys.path.insert(0, str(BACK_DIR))


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")