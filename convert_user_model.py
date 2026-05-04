#!/usr/bin/env python3
"""
Convert user's Teddy Bear FBX model to GLB
Usage: blender --background --python convert_user_model.py
"""

import bpy
import os
from pathlib import Path

# Input FBX file from user
INPUT_FBX = r"F:\研一\Tech Direction\合作项目\Bear O.fbx"

# Output GLB location
OUTPUT_DIR = Path(__file__).parent / "public" / "models" / "teddy"
OUTPUT_GLB = OUTPUT_DIR / "Bear O.glb"

def convert():
    """Convert FBX to GLB"""
    
    # Verify input file exists
    if not os.path.exists(INPUT_FBX):
        print(f"❌ ERROR: Input file not found: {INPUT_FBX}")
        return False
    
    print(f"\n{'='*60}")
    print(f"🔄 Converting Teddy Bear Model")
    print(f"{'='*60}")
    print(f"Input:  {INPUT_FBX}")
    print(f"Output: {OUTPUT_GLB}")
    
    # Create output directory if needed
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        # Clear scene
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        
        # Import FBX
        print(f"\n📥 Importing FBX...")
        bpy.ops.import_scene.fbx(filepath=INPUT_FBX)
        print(f"✓ Import complete")
        
        # Get info about imported objects
        imported_objects = len(bpy.context.scene.objects)
        print(f"📊 Imported {imported_objects} objects")
        
        # Select all objects
        bpy.ops.object.select_all(action='SELECT')
        
        # Export to GLB
        print(f"\n📤 Exporting to GLB...")
        bpy.ops.export_scene.gltf(
            filepath=str(OUTPUT_GLB),
            export_format='GLB',
            export_image_format='AUTO',
            export_animations=True,
            export_frame_range=True
        )
        print(f"✓ Export complete")
        
        # Check output file
        if os.path.exists(OUTPUT_GLB):
            file_size = os.path.getsize(OUTPUT_GLB)
            print(f"\n✅ SUCCESS!")
            print(f"📦 Output file size: {file_size / 1024:.1f} KB")
            print(f"💾 Saved to: {OUTPUT_GLB}")
            return True
        else:
            print(f"❌ ERROR: Output file was not created")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = convert()
    exit(0 if success else 1)
