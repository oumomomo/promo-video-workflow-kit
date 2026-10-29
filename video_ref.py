#!/usr/bin/env python3
"""Repository entry point; the distributable skill is self-contained."""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parent / 'skills/video-reference-kit/scripts/video_ref.py'), run_name='__main__')
