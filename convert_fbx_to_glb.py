#!/usr/bin/env python3
"""
FBX to GLB Converter
Converts all FBX files in public/models to GLB format for Three.js
"""

import bpy
import os
from pathlib import Path

def convert_fbx_to_glb(fbx_file, output_file):
    """Convert FBX file to GLB format"""
    print(f"\n{'='*60}")
    print(f"Converting: {os.path.basename(fbx_file)}")
    print(f"Output: {os.path.basename(output_file)}")
    print(f"{'='*60}")
    
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Import FBX
    print(f"Importing FBX...")
    bpy.ops.import_scene.fbx(filepath=fbx_file)
    
    # Select all objects
    bpy.ops.object.select_all(action='SELECT')
    
    # Export to GLB
    print(f"Exporting to GLB...")
    bpy.ops.export_scene.gltf(
        filepath=output_file,
        export_format='GLB',
        export_image_format='AUTO',
        export_animations=True,
        export_frame_range=True
    )
    
    print(f"✓ Conversion successful!")


def main():
    """Convert all FBX files in public/models"""
    
    # Get script directory
    script_dir = Path(__file__).parent
    models_dir = script_dir / "public" / "models"
    
    # Find all FBX files
    fbx_files = list(models_dir.glob("**/*.fbx"))
    
    if not fbx_files:
        print("❌ No FBX files found in public/models")
        return
    
    print(f"\n🔄 Found {len(fbx_files)} FBX files to convert")
    
    for fbx_file in fbx_files:
        # Create output path (same name, .glb extension)
        output_file = fbx_file.with_suffix('.glb')
        
        try:
            convert_fbx_to_glb(str(fbx_file), str(output_file))
        except Exception as e:
            print(f"❌ Error converting {fbx_file.name}: {e}")
            continue
    
    print(f"\n{'='*60}")
    print(f"✓ Conversion complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
