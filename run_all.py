"""Titik masuk: python run_all.py  (jalankan semua eksperimen)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from tspjawa.eksperimen import main

if __name__ == "__main__":
    main()
