"""
Batch Render Script: FBX Characters with Point Clouds using RadianceField

This script:
1. Imports PLY point cloud files
2. Imports FBX character animations
3. Applies RadianceField geometry nodes
4. Renders all combinations as MP4 videos sequentially
5. Uses GPU rendering (CYCLES engine)

Run with: blender -b --python batch_render_radiancefield.py
"""

from pathlib import Path
from typing import Optional, List, Tuple
import sys

import bpy
from mathutils import Vector

# Configuration
CHARACTERS_FOLDER = Path("./characters")
POINTCLOUDS_FOLDER = Path("./pointclouds")
RADIANCEFIELD_BLEND = Path("./radiancefield.blend")
OUTPUT_FOLDER = Path("./renders")
FPS = 24
QUALITY = "high"  # high, medium, or low

# Rendering parameters
FRAME_STEP = 5  # Bake keyframes every N frames
CAMERA_DISTANCE = 2.5  # Distance from target in meters
CAMERA_HEIGHT_OFFSET = 1.5  # Height above target center
TARGET_BONE_NAME = "mixamorig:Hips"  # Common Mixamo bone name
RENDER_ENGINE = "CYCLES"
USE_GPU = True


def print_header(text: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"🎬 {text}")
    print("=" * 60)


def print_step(text: str) -> None:
    """Print a step message."""
    print(f"\n→ {text}")


def print_success(text: str) -> None:
    """Print a success message."""
    print(f"✓ {text}")


def print_warning(text: str) -> None:
    """Print a warning message."""
    print(f"⚠ {text}")


def print_error(text: str) -> None:
    """Print an error message."""
    print(f"✗ {text}")


def setup_gpu_rendering() -> None:
    """Configure Blender for GPU rendering."""
    print_step("Setting up GPU rendering")
    
    try:
        # Set render engine to CYCLES
        bpy.context.scene.render.engine = "CYCLES"
        
        # Get Cycles preferences
        cycles_prefs = bpy.context.preferences.addons.get('cycles')
        if cycles_prefs:
            prefs = cycles_prefs.preferences
            
            # Try to set CUDA as compute device
            try:
                prefs.compute_device_type = 'CUDA'
                # Enumerate available GPUs
                for device in prefs.devices:
                    device.use = True
                print_success(f"GPU rendering configured with CUDA")
            except Exception as e:
                print_warning(f"Could not configure CUDA: {e}")
                print_warning("Falling back to CPU rendering")
        
        # Cycles settings for quality
        if QUALITY == "high":
            bpy.context.scene.cycles.samples = 256
        elif QUALITY == "medium":
            bpy.context.scene.cycles.samples = 128
        else:
            bpy.context.scene.cycles.samples = 64
        
        # Enable denoising
        bpy.context.scene.cycles.use_denoising = True
        
    except Exception as e:
        print_warning(f"Error setting up GPU: {e}")


def reset_scene() -> None:
    """Reset to a clean scene with proper settings."""
    print_step("Resetting scene")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # TikTok aspect ratio: 9:16 (vertical video)
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_y = 1920
    bpy.context.scene.render.resolution_percentage = 100
    
    # Setup GPU rendering
    setup_gpu_rendering()


def ensure_object_mode() -> None:
    """Ensure we're in object mode."""
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")


def import_ply_pointcloud(ply_path: Path) -> bpy.types.Object:
    """Import PLY point cloud file and return the imported object."""
    if not ply_path.exists():
        print_error(f"PLY file not found: {ply_path}")
        raise RuntimeError(f"PLY file not found: {ply_path}")

    print_step(f"Importing point cloud: {ply_path.name}")

    # Import PLY
    bpy.ops.import_mesh.ply(filepath=str(ply_path))
    pointcloud = bpy.context.active_object
    pointcloud.name = "Pointcloud"
    
    print_success(f"Imported point cloud: {ply_path.name}")
    return pointcloud


def apply_radiancefield(pointcloud: bpy.types.Object, radiancefield_blend: Path) -> None:
    """Apply RadianceField node group to the point cloud."""
    print_step(f"Applying RadianceField to {pointcloud.name}")
    
    if not radiancefield_blend.exists():
        print_error(f"radiancefield.blend not found: {radiancefield_blend}")
        raise RuntimeError(f"radiancefield.blend not found: {radiancefield_blend}")
    
    try:
        # Link the RadianceField node group from the blend file
        with bpy.data.libraries.load(str(radiancefield_blend), link=False) as (data_from, data_to):
            if "RadianceField" in data_from.node_groups:
                data_to.node_groups.append("RadianceField")
                print_success("RadianceField node group loaded")
            else:
                print_warning("RadianceField node group not found in blend file")
                print(f"Available node groups: {data_from.node_groups}")
                return
        
        # Get the RadianceField node group
        if "RadianceField" in bpy.data.node_groups:
            radiancefield_group = bpy.data.node_groups["RadianceField"]
            
            # Add Geometry Nodes modifier
            if "GeometryNodes" not in pointcloud.modifiers:
                mod = pointcloud.modifiers.new(name="GeometryNodes", type='GEOMETRY_NODES')
                mod.node_group = radiancefield_group
                print_success("RadianceField geometry nodes applied")
            else:
                mod = pointcloud.modifiers["GeometryNodes"]
                mod.node_group = radiancefield_group
                print_success("RadianceField geometry nodes updated")
        else:
            print_error("RadianceField node group not found after loading")
            raise RuntimeError("RadianceField node group not found")
    
    except Exception as e:
        print_error(f"Error applying RadianceField: {e}")
        raise


def import_fbx(fbx_path: Path) -> List[bpy.types.Object]:
    """Import FBX file and return imported objects."""
    if not fbx_path.exists():
        print_error(f"FBX file not found: {fbx_path}")
        raise RuntimeError(f"FBX file not found: {fbx_path}")

    print_step(f"Importing FBX: {fbx_path.name}")

    # Get objects before import
    objects_before = set(bpy.data.objects)

    # Import FBX
    bpy.ops.import_scene.fbx(filepath=str(fbx_path))

    # Get newly imported objects
    objects_after = set(bpy.data.objects)
    imported_objects = list(objects_after - objects_before)

    print_success(f"Imported {len(imported_objects)} objects from FBX")
    return imported_objects


def find_armature(imported_objects: List[bpy.types.Object]) -> Optional[bpy.types.Object]:
    """Find the armature object from imported objects."""
    for obj in imported_objects:
        if obj.type == "ARMATURE":
            return obj
    return None


def get_target_world_location(
    armature: bpy.types.Object, bone_name: str
) -> Tuple[float, float, float]:
    """Get world location of a bone in the armature."""
    if bone_name in armature.pose.bones:
        bone = armature.pose.bones[bone_name]
        matrix = armature.matrix_world @ bone.matrix
        return tuple(matrix.translation)
    return tuple(armature.matrix_world.translation)


def create_tiktok_camera(name: str = "TikTokCamera") -> bpy.types.Object:
    """Create a camera optimized for TikTok-style vertical video."""
    bpy.ops.object.camera_add()
    camera = bpy.context.active_object
    camera.name = name
    camera.data.name = f"{name}_data"

    # Camera settings for portrait video
    camera.data.lens = 50
    camera.data.sensor_width = 36
    camera.data.sensor_height = 36 * (16 / 9)

    # Set as active camera
    bpy.context.scene.camera = camera

    return camera


def setup_camera_tracking(
    camera: bpy.types.Object,
    target: bpy.types.Object,
    bone_name: Optional[str] = None,
    frame_start: int = 1,
    frame_end: int = 250,
) -> None:
    """Setup camera to follow the target with baked keyframes."""
    print_step(f"Setting up camera tracking from frame {frame_start} to {frame_end}")

    # Clear existing animation data
    if camera.animation_data:
        camera.animation_data_clear()

    scene = bpy.context.scene

    # Bake keyframes
    for frame in range(frame_start, frame_end + 1, FRAME_STEP):
        scene.frame_set(frame)

        # Get target location
        if target.type == "ARMATURE" and bone_name:
            target_loc = get_target_world_location(target, bone_name)
        else:
            target_loc = tuple(target.matrix_world.translation)

        # Position camera behind and above target
        camera.location = (
            target_loc[0],
            target_loc[1] - CAMERA_DISTANCE,
            target_loc[2] + CAMERA_HEIGHT_OFFSET,
        )

        # Point camera at target
        direction = Vector(
            (
                target_loc[0] - camera.location[0],
                target_loc[1] - camera.location[1],
                target_loc[2] - camera.location[2],
            )
        )

        # Calculate rotation to look at target
        track_quat = direction.to_track_quat("-Z", "Y")
        camera.rotation_euler = track_quat.to_euler()

        # Insert keyframes
        camera.keyframe_insert(data_path="location", frame=frame)
        camera.keyframe_insert(data_path="rotation_euler", frame=frame)

    print_success(f"Baked {(frame_end - frame_start) // FRAME_STEP + 1} keyframes")


def add_studio_lighting() -> None:
    """Add basic three-point lighting setup."""
    print_step("Adding studio lighting")

    # Key light
    bpy.ops.object.light_add(type="AREA", location=(2, -2, 4))
    key_light = bpy.context.active_object
    key_light.name = "KeyLight"
    key_light.data.energy = 200
    key_light.data.size = 2

    # Fill light
    bpy.ops.object.light_add(type="AREA", location=(-2, -1, 2))
    fill_light = bpy.context.active_object
    fill_light.name = "FillLight"
    fill_light.data.energy = 100
    fill_light.data.size = 2

    # Rim light
    bpy.ops.object.light_add(type="SPOT", location=(0, 2, 3))
    rim_light = bpy.context.active_object
    rim_light.name = "RimLight"
    rim_light.data.energy = 150

    print_success("Lighting setup complete")


def render_to_mp4(
    output_path: Path,
    fps: int = 24,
    quality: str = "high",
    frame_start: Optional[int] = None,
    frame_end: Optional[int] = None,
) -> Path:
    """Render animation to MP4 using GPU."""
    scene = bpy.context.scene
    
    if frame_start is None:
        frame_start = scene.frame_start
    if frame_end is None:
        frame_end = scene.frame_end
    
    print_step(f"Rendering frames {frame_start} to {frame_end} ({RENDER_ENGINE})")
    
    # Store original settings
    original_media_type = scene.render.image_settings.media_type
    original_format = scene.render.image_settings.file_format
    original_filepath = scene.render.filepath
    original_start = scene.frame_start
    original_end = scene.frame_end
    
    try:
        # Configure FFmpeg output
        scene.render.image_settings.media_type = 'VIDEO'
        scene.render.image_settings.file_format = 'FFMPEG'
        scene.render.ffmpeg.format = 'MPEG4'
        scene.render.ffmpeg.codec = 'H264'
        
        # Quality settings
        bitrate_map = {"high": 8000, "medium": 4000, "low": 2000}
        crf_map = {"high": 'HIGH', "medium": 'MEDIUM', "low": 'LOW'}
        
        scene.render.ffmpeg.constant_rate_factor = crf_map.get(quality, 'MEDIUM')
        scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
        scene.render.ffmpeg.video_bitrate = bitrate_map.get(quality, 4000)
        scene.render.ffmpeg.gopsize = 12 if quality == 'high' else 15 if quality == 'medium' else 18
        
        scene.render.ffmpeg.audio_codec = 'AAC'
        scene.render.ffmpeg.audio_bitrate = 192
        
        # Frame rate
        scene.render.fps = fps
        scene.render.fps_base = 1.0
        
        # Set output path and frame range
        output_path = output_path.resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        scene.render.filepath = str(output_path)
        scene.frame_start = frame_start
        scene.frame_end = frame_end
        
        print(f"Output: {scene.render.filepath}")
        
        # Render animation
        bpy.ops.render.render(animation=True, write_still=False)
        
        print_success(f"MP4 rendered: {output_path}")
        
        if output_path.exists():
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            duration = (frame_end - frame_start + 1) / fps
            print(f"  Size: {file_size_mb:.2f} MB | Duration: {duration:.2f}s")
        
    except Exception as e:
        print_error(f"Rendering error: {e}")
        raise
    finally:
        # Restore original settings
        scene.render.image_settings.media_type = original_media_type
        scene.render.image_settings.file_format = original_format
        scene.render.filepath = original_filepath
        scene.frame_start = original_start
        scene.frame_end = original_end
    
    return output_path


def remove_imported_objects(imported_objects: List[bpy.types.Object]) -> None:
    """Remove imported objects from the scene."""
    ensure_object_mode()
    for obj in imported_objects:
        if obj.name in bpy.data.objects:
            bpy.data.objects.remove(obj, do_unlink=True)


def batch_render(
    characters_folder: Path,
    pointclouds_folder: Path,
    radiancefield_blend: Path,
    output_folder: Path,
) -> None:
    """Batch render all FBX + point cloud combinations."""
    
    print_header("Batch Render with RadianceField")
    
    # Validate folders
    if not characters_folder.exists():
        print_error(f"Characters folder not found: {characters_folder}")
        return
    
    if not pointclouds_folder.exists():
        print_error(f"Pointclouds folder not found: {pointclouds_folder}")
        return
    
    if not radiancefield_blend.exists():
        print_error(f"radiancefield.blend not found: {radiancefield_blend}")
        return
    
    # Collect FBX and PLY files in order
    fbx_files = sorted([f for f in characters_folder.glob("*.fbx") if f.name in [
        "doozy-hiphop.fbx", "vegas-hiphop.fbx", "michelle-hiphop.fbx", "mouse-hiphop.fbx"
    ]])
    ply_files = sorted([f for f in pointclouds_folder.glob("*.ply")])
    
    print(f"\nFound {len(fbx_files)} FBX files:")
    for f in fbx_files:
        print(f"  - {f.name}")
    
    print(f"\nFound {len(ply_files)} PLY files:")
    for f in ply_files:
        print(f"  - {f.name}")
    
    if not fbx_files or not ply_files:
        print_error("No FBX or PLY files found")
        return
    
    output_folder.mkdir(parents=True, exist_ok=True)
    
    total_renders = len(fbx_files) * len(ply_files)
    current_render = 1
    
    # Process each FBX file with each PLY file
    for fbx_file in fbx_files:
        for ply_file in ply_files:
            print_header(f"[{current_render}/{total_renders}] {fbx_file.stem} + {ply_file.stem}")
            
            try:
                # Reset scene
                reset_scene()
                ensure_object_mode()
                
                # Import point cloud
                pointcloud = import_ply_pointcloud(ply_file)
                
                # Apply RadianceField
                apply_radiancefield(pointcloud, radiancefield_blend)
                
                # Import FBX character
                fbx_objects = import_fbx(fbx_file)
                
                # Find armature and determine end frame
                armature = find_armature(fbx_objects)
                frame_start = 1
                if armature:
                    if armature.animation_data and armature.animation_data.action:
                        frame_end = int(armature.animation_data.action.frame_range[1])
                    else:
                        frame_end = 250
                    bpy.context.scene.frame_start = frame_start
                    bpy.context.scene.frame_end = frame_end
                    target = armature
                    target_bone = TARGET_BONE_NAME
                else:
                    print_warning("No armature found in FBX")
                    frame_end = 250
                    bpy.context.scene.frame_start = frame_start
                    bpy.context.scene.frame_end = frame_end
                    target = fbx_objects[0] if fbx_objects else None
                    target_bone = None
                
                # Create camera
                print_step("Creating camera")
                camera = create_tiktok_camera()
                
                # Setup camera tracking
                if target:
                    setup_camera_tracking(camera, target, target_bone, frame_start, frame_end)
                
                # Add lighting
                add_studio_lighting()
                
                # Render to MP4
                output_file = output_folder / f"{fbx_file.stem}_{ply_file.stem}.mp4"
                print_step(f"Rendering output: {output_file}")
                render_to_mp4(output_file, fps=FPS, quality=QUALITY, frame_start=frame_start, frame_end=frame_end)
                
                print_success(f"Rendered: {output_file.name}")
                
            except Exception as e:
                print_error(f"Error rendering {fbx_file.stem} + {ply_file.stem}: {e}")
                import traceback
                traceback.print_exc()
                continue
            
            finally:
                current_render += 1
    
    print_header(f"✨ Batch rendering complete! All {total_renders} videos saved")


def main():
    """Main execution."""
    # Use absolute paths from the script directory
    script_dir = Path(__file__).parent.absolute()
    
    characters_folder = script_dir / ".." / ".." / "characters"
    pointclouds_folder = script_dir / ".." / ".." / "pointclouds"
    radiancefield_blend = script_dir / "radiancefield.blend"
    output_folder = script_dir / "renders"
    
    # Make paths absolute
    characters_folder = characters_folder.resolve()
    pointclouds_folder = pointclouds_folder.resolve()
    radiancefield_blend = radiancefield_blend.resolve()
    output_folder = output_folder.resolve()
    
    batch_render(characters_folder, pointclouds_folder, radiancefield_blend, output_folder)


if __name__ == "__main__":
    main()
