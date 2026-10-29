#!/usr/bin/env python3
"""Project-local entry point; the skill also runs independently of this wrapper."""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parent / 'skills/video-making-kit/scripts/video_make.py'), run_name='__main__')
