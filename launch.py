#!/usr/bin/env python3

import os
import sys

# Add project root to Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# Import and run video instrument
from video_instrument import VideoInstrument

def main():
    app = VideoInstrument()
    try:
        app.load_scripts()
        app.switch_script("pattern_00")
        print("Starting Video Instrument...")
        app.run()
    except Exception as e:
        print(f"Error running Video Instrument: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Video Instrument closed")

if __name__ == "__main__":
    main()