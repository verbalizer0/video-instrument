# run.py

import os
import sys
from pathlib import Path

# Get absolute path of project root
project_root = os.path.dirname(os.path.abspath(__file__))
print(f"Project root: {project_root}")

# Add to Python path
sys.path.insert(0, project_root)
print(f"Python path: {sys.path}")

# Check if key directories exist
patterns_dir = os.path.join(project_root, 'patterns')
visuals_dir = os.path.join(project_root, 'visuals')
print(f"\nChecking directories:")
print(f"Patterns directory exists: {os.path.exists(patterns_dir)}")
print(f"Visuals directory exists: {os.path.exists(visuals_dir)}")

# List pattern files
print("\nPattern files found:")
if os.path.exists(patterns_dir):
    pattern_files = [f for f in os.listdir(patterns_dir) if f.endswith('.py')]
    for file in pattern_files:
        print(f"  - {file}")

# Try importing with debug info
print("\nAttempting imports:")
try:
    print("Importing video_instrument...")
    from video_instrument import VideoInstrument
    print("Successfully imported VideoInstrument")
    
    print("\nImporting visuals.backgrounds.original_modes...")
    try:
        from visuals.backgrounds.original_modes import BackgroundManagerExtended
        print("Successfully imported BackgroundManagerExtended")
    except Exception as e:
        print(f"Error importing BackgroundManagerExtended: {e}")
        
    print("\nInitializing application...")
    app = VideoInstrument()
    
    print("\nLoading scripts...")
    app.load_scripts()
    
    print("\nStarting Video Instrument...")
    app.switch_script("pattern_00")
    app.run()
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    print("\nVideo Instrument closed")