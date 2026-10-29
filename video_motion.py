#!/usr/bin/env python3
"""Distribution motion kit entry; the complete skill folder also runs on its own."""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parent / 'skills/video-motion-kit/scripts/motion.py'), run_name='__main__')
