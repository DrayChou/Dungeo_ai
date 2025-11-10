#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Dungeon Master Adventure - GUI主入口文件
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the GUI main game
from dungeona_ai.gui.gui import main as gui_main

if __name__ == "__main__":
    gui_main()