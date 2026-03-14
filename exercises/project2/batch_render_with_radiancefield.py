"""
Batch Render Script: FBX Characters with Point Clouds using RadianceField

This script:
1. Imports PLY point cloud files
2. Imports FBX character animations
3. Applies RadianceField geometry nodes
4. Renders all combinations as MP4 videos sequentially
5. Uses GPU rendering
"""

from pathlib import Path
from typing import Optional, List, Tuple
import sys

import bpy
import typer
from mathutils import Vector

app = typer.Typer(help="Batch render FBX + Point Cloud combinations with RadianceField")

# Configuration
FRAME_STEP = 5  # Bake keyframes every N frames
CAMERA_DISTANCE = 2.5  # Distance from target in meters
CAMERA_HEIGHT_OFFSET = 1.5  # Height above target center
TARGET_BONE_NAME = "mixamorig:Hips"  # Common Mixamo bone name
RENDER_ENGINE = "CYCLES"  # Use CYCLES for GPU rendering
USE_GPU = True  # Enable GPU rendering


def setup_gpu_rendering() -> None:
    """Configure Blender for GPU rendering."""
    typer.echo("Setting up GPU rendering...")
    
    try:
        # Set render engine to CYCLES (supports GPU)
        bpy.context.scene.render.engine = "CYCLES"
        bpy.context.scene.cycles.use_denoising = True
        
        # Try to enable GPU rendering with CUDA
        try:
            prefs = bpy.context.preferences.addons['cycles'].preferences
            
            # Detect available compute devices
            prefs.compute_device_type = 'CUDA'
            
            # Enable all available CUDA devices
            for device in prefs.devices:
                device.use = True
            
            # Enable GPU samples
            bpy.context.scene.cycles.device = 'GPU'
            
            typer.secho("✓ CUDA GPU rendering enabled", fg=typer.colors.GREEN)
        except Exception as e:
            typer.secho(f"⚠ Could not enable CUDA GPU, falling back to CPU: {e}", fg=typer.colors.YELLOW)
            bpy.context.scene.cycles.device = 'CPU'
        
        # Other optimization settings
        bpy.context.scene.cycles.use_denoising = True
        bpy.context.scene.cycles.denoising_use_gpu = True
        
        # Reduce samples for faster rendering while maintaining quality
        bpy.context.scene.cycles.samples = 128
        bpy.context.scene.cycles.preview_samples = 64
        
        typer.secho("✓ GPU rendering configured", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"Warning: GPU setup error: {e}", fg=typer.colors.YELLOW)


def reset_scene() -> None:
    """Reset to a clean scene with proper settings."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # TikTok aspect ratio: 9:16 (vertical video)
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_y = 1920
    bpy.context.scene.render.resolution_percentage = 25
    
    # Setup GPU rendering
    setup_gpu_rendering()


def ensure_object_mode() -> None:
    """Ensure we're in object mode."""
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")


def import_ply_pointcloud(ply_path: Path) -> bpy.types.Object:
    """Import PLY point cloud file and return the imported object."""
    if not ply_path.exists():
        typer.secho(f"Error: PLY file not found: {ply_path}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.echo(f"Importing point cloud: {ply_path.name}")

    # Import PLY
    bpy.ops.import_mesh.ply(filepath=str(ply_path))
    pointcloud = bpy.context.active_object
    pointcloud.name = "Pointcloud"
    
    typer.secho(f"✓ Imported point cloud: {ply_path.name}", fg=typer.colors.GREEN)
    return pointcloud


def apply_radiancefield(pointcloud: bpy.types.Object, radiancefield_blend: Path) -> None:
    """Apply RadianceField node group to the point cloud."""
    typer.echo(f"Applying RadianceField to {pointcloud.name}...")
    
    if not radiancefield_blend.exists():
        typer.secho(f"Error: radiancefield.blend not found: {radiancefield_blend}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    
    # Link the RadianceField node group from the blend file
    with bpy.data.libraries.load(str(radiancefield_blend), link=False) as (data_from, data_to):
        if "RadianceField" in data_from.node_groups:
            data_to.node_groups.append("RadianceField")
            typer.secho("✓ RadianceField node group loaded from blend file", fg=typer.colors.GREEN)
        else:
            typer.secho("Warning: RadianceField node group not found in blend file", fg=typer.colors.YELLOW)
            typer.echo(f"Available node groups: {data_from.node_groups}")
            return
    
    # Get the RadianceField node group
    if "RadianceField" in bpy.data.node_groups:
        radiancefield_group = bpy.data.node_groups["RadianceField"]
        
        # Add Geometry Nodes modifier
        if "GeometryNodes" not in pointcloud.modifiers:
            mod = pointcloud.modifiers.new(name="GeometryNodes", type='GEOMETRY_NODES')
            mod.node_group = radiancefield_group
            typer.secho("✓ RadianceField geometry nodes applied", fg=typer.colors.GREEN)
        else:
            mod = pointcloud.modifiers["GeometryNodes"]
            mod.node_group = radiancefield_group
            typer.secho("✓ RadianceField geometry nodes updated", fg=typer.colors.GREEN)
    else:
        typer.secho("Error: RadianceField node group not found after loading", fg=typer.colors.RED)
        raise typer.Exit(code=1)


def import_fbx(fbx_path: Path) -> List[bpy.types.Object]:
    """Import FBX file and return imported objects."""
    if not fbx_path.exists():
        typer.secho(f"Error: FBX file not found: {fbx_path}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.echo(f"Importing FBX: {fbx_path.name}")

    # Get objects before import
    objects_before = set(bpy.data.objects)

    # Import FBX
    bpy.ops.import_scene.fbx(filepath=str(fbx_path))

    # Get newly imported objects
    objects_after = set(bpy.data.objects)
    imported_objects = list(objects_after - objects_before)

    typer.secho(f"✓ Imported {len(imported_objects)} objects from FBX", fg=typer.colors.GREEN)
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
    typer.echo(f"Setting up camera tracking from frame {frame_start} to {frame_end}...")

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

    typer.secho(
        f"✓ Baked {(frame_end - frame_start) // FRAME_STEP + 1} keyframes",
        fg=typer.colors.GREEN,
    )


def add_studio_lighting() -> None:
    """Add basic three-point lighting setup."""
    typer.echo("Adding studio lighting...")

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

    typer.secho("✓ Lighting setup complete", fg=typer.colors.GREEN)


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
    
    typer.echo(f"Rendering frames {frame_start} to {frame_end} (GPU)...")
    
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
        
        # Quality settings based on CYCLES
        if quality == 'high':
            bpy.context.scene.cycles.samples = 256
            bpy.context.scene.cycles.preview_samples = 128
        elif quality == 'medium':
            bpy.context.scene.cycles.samples = 128
        else:
            bpy.context.scene.cycles.samples = 64
        
        scene.render.ffmpeg.constant_rate_factor = 'HIGH' if quality == 'high' else 'MEDIUM' if quality == 'medium' else 'LOW'
        scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
        scene.render.ffmpeg.video_bitrate = 8000 if quality == 'high' else 4000 if quality == 'medium' else 2000
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
        
        typer.echo(f"Output: {scene.render.filepath}")
        
        # Render animation
        bpy.ops.render.render(animation=True, write_still=False)
        
        typer.secho(f"✓ MP4 rendered: {output_path}", fg=typer.colors.GREEN)
        
        if output_path.exists():
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            typer.echo(f"  Size: {file_size_mb:.2f} MB")
            typer.echo(f"  Resolution: {scene.render.resolution_x}x{scene.render.resolution_y}")
            typer.echo(f"  Duration: {(frame_end - frame_start + 1) / fps:.2f}s")
        
    except Exception as e:
        typer.secho(f"Error during rendering: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
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


@app.command()
def batch_render(
    characters_folder: Path = typer.Argument(help="Path to characters folder with FBX files"),
    pointclouds_folder: Path = typer.Argument(help="Path to pointclouds folder with PLY files"),
    radiancefield_blend: Path = typer.Argument(help="Path to radiancefield.blend"),
    output_folder: Path = typer.Option(Path("./renders"), "--output", "-o", help="Output folder for MP4 files"),
    fps: int = typer.Option(24, "--fps", help="Frames per second"),
    quality: str = typer.Option("high", "--quality", "-q", help="Quality: high, medium, or low"),
) -> None:
    """
    Batch render FBX characters with point clouds using RadianceField.
    
    Renders each FBX character with each point cloud sequentially.
    Process: doozy-hiphop (all 5 clouds) → vegas-hiphop (all 5) → michelle-hiphop (all 5) → mouse-hiphop (all 5)
    
    Example:
        python batch_render_with_radiancefield.py ./characters ./pointclouds ./radiancefield.blend
    """
    typer.secho("🎬 Batch Render with RadianceField", fg=typer.colors.CYAN, bold=True)
    typer.echo("=" * 60)
    
    # Validate folders and files
    if not characters_folder.exists():
        typer.secho(f"Error: Characters folder not found: {characters_folder}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    
    if not pointclouds_folder.exists():
        typer.secho(f"Error: Pointclouds folder not found: {pointclouds_folder}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    
    if not radiancefield_blend.exists():
        typer.secho(f"Error: radiancefield.blend not found: {radiancefield_blend}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    
    # Collect FBX and PLY files in specified order
    fbx_order = ["doozy-hiphop.fbx", "vegas-hiphop.fbx", "michelle-hiphop.fbx", "mouse-hiphop.fbx"]
    fbx_files = [characters_folder / name for name in fbx_order if (characters_folder / name).exists()]
    
    # PLY files in specified order
    ply_order = [
        "Mailbox_point_cloud.ply",
        "Hydrant_vertical_point_cloud.ply",
        "David_Bust_point_cloud.ply",
        "McLaren_point_cloud.ply",
        "Panzernashorn_Tobler_point_cloud.ply"
    ]
    ply_files = [pointclouds_folder / name for name in ply_order if (pointclouds_folder / name).exists()]
    
    typer.echo(f"Found {len(fbx_files)} FBX files")
    for f in fbx_files:
        typer.echo(f"  - {f.name}")
    
    typer.echo(f"\nFound {len(ply_files)} PLY files")
    for f in ply_files:
        typer.echo(f"  - {f.name}")
    
    if not fbx_files:
        typer.secho("Error: No FBX files found", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    
    if not ply_files:
        typer.secho("Error: No PLY files found", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    
    output_folder.mkdir(parents=True, exist_ok=True)
    
    total_renders = len(fbx_files) * len(ply_files)
    current_render = 1
    
    # Process each FBX file with each PLY file
    for fbx_file in fbx_files:
        for ply_file in ply_files:
            typer.secho(f"\n[{current_render}/{total_renders}] {fbx_file.stem} + {ply_file.stem}", fg=typer.colors.CYAN, bold=True)
            
            try:
                # Reset scene
                typer.echo("Resetting scene...")
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
                if armature:
                    bpy.context.scene.frame_start = 1
                    if armature.animation_data and armature.animation_data.action:
                        frame_end = int(armature.animation_data.action.frame_range[1])
                    else:
                        frame_end = 250
                    bpy.context.scene.frame_end = frame_end
                    target = armature
                    target_bone = TARGET_BONE_NAME
                else:
                    typer.secho("Warning: No armature found in FBX", fg=typer.colors.YELLOW)
                    frame_end = 250
                    bpy.context.scene.frame_start = 1
                    bpy.context.scene.frame_end = frame_end
                    target = fbx_objects[0] if fbx_objects else None
                    target_bone = None
                
                # Create camera
                typer.echo("Creating camera...")
                camera = create_tiktok_camera()
                
                # Setup camera tracking
                if target:
                    setup_camera_tracking(camera, target, target_bone, 1, frame_end)
                
                # Add lighting
                add_studio_lighting()
                
                # Render to MP4
                output_file = output_folder / f"{fbx_file.stem}_{ply_file.stem}.mp4"
                typer.echo(f"\nRendering to: {output_file}")
                render_to_mp4(output_file, fps=fps, quality=quality, frame_start=1, frame_end=frame_end)
                
                typer.secho(f"✓ Completed: {output_file.name}", fg=typer.colors.GREEN)
                
            except Exception as e:
                typer.secho(f"✗ Error rendering {fbx_file.stem} + {ply_file.stem}: {e}", fg=typer.colors.RED)
                continue
            
            finally:
                current_render += 1
    
    typer.echo("\n" + "=" * 60)
    typer.secho(f"✨ Batch rendering complete! All {total_renders} videos saved to: {output_folder}", fg=typer.colors.GREEN, bold=True)


if __name__ == "__main__":
    app()
