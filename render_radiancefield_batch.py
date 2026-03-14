#!/usr/bin/env python3
"""
Batch render FBX characters with point clouds using RadianceField.
Run in Blender: blender --background -P this_script.py

This script:
1. Imports PLY point cloud files
2. Imports FBX character animations
3. Applies RadianceField geometry nodes
4. Renders all combinations as MP4 videos sequentially
5. Uses GPU rendering with CYCLES engine
"""

from pathlib import Path
import bpy
from mathutils import Vector
import struct
import bmesh

# Configuration
CHARACTERS_PATH = Path(r"f:\研一\Tech Direction\tdspring26\tdspring26\characters")
POINTCLOUDS_PATH = Path(r"f:\研一\Tech Direction\tdspring26\tdspring26\pointclouds")
RADIANCEFIELD_BLEND = Path(r"f:\研一\Tech Direction\tdspring26\tdspring26\exercises\project2\radiancefield.blend")
OUTPUT_PATH = Path(r"f:\研一\Tech Direction\tdspring26\tdspring26\exercises\project2\videos")

FRAME_STEP = 5
CAMERA_DISTANCE = 2.5
CAMERA_HEIGHT_OFFSET = 1.5
TARGET_BONE_NAME = "mixamorig:Hips"

def log(message: str, level="INFO"):
    """Print log message."""
    prefix = f"[{level}]"
    print(f"{prefix} {message}")

def setup_gpu_rendering() -> None:
    """Configure Blender for GPU rendering."""
    log("Setting up GPU rendering...")
    
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
            log("✓ CUDA GPU rendering enabled", "SUCCESS")
        except Exception as e:
            log(f"⚠ Could not enable CUDA GPU, falling back to CPU: {e}", "WARNING")
            bpy.context.scene.cycles.device = 'CPU'
        
        # Other optimization settings
        bpy.context.scene.cycles.use_denoising = True
        bpy.context.scene.cycles.denoising_use_gpu = True
        
        # Samples
        bpy.context.scene.cycles.samples = 128
        bpy.context.scene.cycles.preview_samples = 64
        
        log("✓ GPU rendering configured", "SUCCESS")
    except Exception as e:
        log(f"Warning: GPU setup error: {e}", "WARNING")

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

def parse_ply_header(filename: str) -> tuple:
    """Parse PLY file header to get vertex/face counts and format."""
    vertex_count = 0
    face_count = 0
    is_binary = False
    
    with open(filename, 'rb') as f:
        line = f.readline().decode().strip()
        if line != 'ply':
            raise ValueError("File is not a valid PLY file")
        
        while True:
            line = f.readline().decode().strip()
            if not line:
                continue
            
            if line.startswith('format'):
                if 'binary_little_endian' in line:
                    is_binary = True
                elif 'binary_big_endian' in line:
                    is_binary = True
            elif line.startswith('element vertex'):
                vertex_count = int(line.split()[-1])
            elif line.startswith('element face'):
                face_count = int(line.split()[-1])
            elif line == 'end_header':
                break
    
    return vertex_count, face_count, is_binary

def import_ply_file(ply_path: Path) -> list:
    """Import PLY file by parsing it properly (binary or ASCII)."""
    log(f"Parsing PLY file: {ply_path.name}")
    
    try:
        # Create empty mesh and object  
        mesh = bpy.data.meshes.new("Pointcloud_Mesh")
        obj = bpy.data.objects.new("Pointcloud", mesh)
        bpy.context.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Parse PLY file
        vertices = []
        faces = []
        
        with open(ply_path, 'rb') as f:
            # Read header
            header_lines = []
            while True:
                line = f.readline()
                try:
                    line_str = line.decode('ascii').strip()
                except:
                    log(f"Error decoding PLY header line", "WARNING")
                    continue
                    
                header_lines.append(line_str)
                if line_str == 'end_header':
                    break
            
            # Parse header
            vertex_count = 0
            face_count = 0
            is_binary = False
            byte_order = '<'  # little-endian by default
            
            for line in header_lines:
                if line.startswith('format'):
                    if 'binary_little_endian' in line:
                        is_binary = True
                        byte_order = '<'
                    elif 'binary_big_endian' in line:
                        is_binary = True
                        byte_order = '>'
                elif line.startswith('element vertex'):
                    vertex_count = int(line.split()[-1])
                elif line.startswith('element face'):
                    face_count = int(line.split()[-1])
            
            log(f"  Format: {'binary' if is_binary else 'text'}, Vertices: {vertex_count}, Faces: {face_count}")
            
            # Read vertex data
            if is_binary:
                # Binary format - read each vertex as 3 floats
                float_size = 4
                for _ in range(vertex_count):
                    data = f.read(float_size * 3)
                    if len(data) == float_size * 3:
                        x, y, z = struct.unpack(f'{byte_order}fff', data)
                        vertices.append((x, y, z))
            else:
                # ASCII format
                for _ in range(vertex_count):
                    line = f.readline().decode('ascii').strip()
                    if line:
                        coords = [float(x) for x in line.split()[:3]]
                        vertices.append(tuple(coords))
            
            # Read face data
            if is_binary:
                # Binary faces: uchar count + indices
                for _ in range(face_count):
                    count_byte = f.read(1)
                    if count_byte:
                        count = struct.unpack(f'{byte_order}B', count_byte)[0]
                        indices_data = f.read(count * 4)
                        if len(indices_data) == count * 4:
                            indices = struct.unpack(f'{byte_order}' + f'I' * count, indices_data)
                            faces.append(list(indices))
            else:
                # ASCII faces
                for _ in range(face_count):
                    line = f.readline().decode('ascii').strip()
                    if line:
                        parts = line.split()
                        n_verts = int(parts[0])
                        face_verts = [int(parts[i+1]) for i in range(n_verts)]
                        faces.append(face_verts)
        
        # Create mesh from vertices and faces
        if vertices:
            mesh.from_pydata(vertices, [], faces)
            mesh.update()
            log(f"✓ PLY file imported: {ply_path.name} ({len(vertices)} vertices, {len(faces)} faces)", "SUCCESS")
        
        return [obj]
        
    except Exception as e:
        log(f"Error importing PLY: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        raise

def import_ply_pointcloud(ply_path: Path) -> bpy.types.Object:
    """Import PLY point cloud file and return the imported object."""
    if not ply_path.exists():
        log(f"Error: PLY file not found: {ply_path}", "ERROR")
        raise RuntimeError(f"PLY file not found: {ply_path}")
    
    log(f"Importing point cloud: {ply_path.name}")
    
    try:
        objects = import_ply_file(ply_path)
        pointcloud = objects[0] if objects else None
        
        if pointcloud:
            pointcloud.name =  "Pointcloud"
            log(f"✓ Imported point cloud: {ply_path.name}", "SUCCESS")
            return pointcloud
        else:
            raise RuntimeError("Failed to import PLY file")
    except Exception as e:
        log(f"Error importing PLY: {e}", "ERROR")
        raise

def apply_radiancefield(pointcloud: bpy.types.Object, radiancefield_blend: Path) -> None:
    """Apply RadianceField node group to the point cloud."""
    log(f"Applying RadianceField to {pointcloud.name}...")
    
    if not radiancefield_blend.exists():
        log(f"Error: radiancefield.blend not found: {radiancefield_blend}", "ERROR")
        raise RuntimeError(f"radiancefield.blend not found: {radiancefield_blend}")
    
    # Link the RadianceField node group from the blend file
    with bpy.data.libraries.load(str(radiancefield_blend), link=False) as (data_from, data_to):
        if "RadianceField" in data_from.node_groups:
            data_to.node_groups.append("RadianceField")
            log("✓ RadianceField node group loaded from blend file", "SUCCESS")
        else:
            log("Warning: RadianceField node group not found in blend file", "WARNING")
            log(f"Available node groups: {data_from.node_groups}", "INFO")
            return
    
    # Get the RadianceField node group
    if "RadianceField" in bpy.data.node_groups:
        radiancefield_group = bpy.data.node_groups["RadianceField"]
        
        # Add Geometry Nodes modifier (called "NODES" in Blender 5.0)
        modifier_type = 'NODES'
        if modifier_type not in pointcloud.modifiers:
            mod = pointcloud.modifiers.new(name="GeometryNodes", type=modifier_type)
            mod.node_group = radiancefield_group
            log("✓ RadianceField geometry nodes applied", "SUCCESS")
        else:
            mod = pointcloud.modifiers[modifier_type]
            mod.node_group = radiancefield_group
            log("✓ RadianceField geometry nodes updated", "SUCCESS")
    else:
        log("Error: RadianceField node group not found after loading", "ERROR")
        raise RuntimeError("RadianceField node group not found after loading")

def import_fbx(fbx_path: Path) -> list:
    """Import FBX file and return imported objects."""
    if not fbx_path.exists():
        log(f"Error: FBX file not found: {fbx_path}", "ERROR")
        raise RuntimeError(f"FBX file not found: {fbx_path}")
    
    log(f"Importing FBX: {fbx_path.name}")
    
    objects_before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(fbx_path))
    objects_after = set(bpy.data.objects)
    imported_objects = list(objects_after - objects_before)
    
    log(f"✓ Imported {len(imported_objects)} objects from FBX", "SUCCESS")
    return imported_objects

def find_armature(imported_objects: list) -> bpy.types.Object or None:
    """Find the armature object from imported objects."""
    for obj in imported_objects:
        if obj.type == "ARMATURE":
            return obj
    return None

def get_target_world_location(armature: bpy.types.Object, bone_name: str) -> tuple:
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
    
    camera.data.lens = 50
    camera.data.sensor_width = 36
    camera.data.sensor_height = 36 * (16 / 9)
    
    bpy.context.scene.camera = camera
    return camera

def setup_camera_tracking(
    camera: bpy.types.Object,
    target: bpy.types.Object,
    bone_name: str = None,
    frame_start: int = 1,
    frame_end: int = 250,
) -> None:
    """Setup camera to follow the target with baked keyframes."""
    log(f"Setting up camera tracking from frame {frame_start} to {frame_end}...")
    
    if camera.animation_data:
        camera.animation_data_clear()
    
    scene = bpy.context.scene
    
    for frame in range(frame_start, frame_end + 1, FRAME_STEP):
        scene.frame_set(frame)
        
        if target.type == "ARMATURE" and bone_name:
            target_loc = get_target_world_location(target, bone_name)
        else:
            target_loc = tuple(target.matrix_world.translation)
        
        camera.location = (
            target_loc[0],
            target_loc[1] - CAMERA_DISTANCE,
            target_loc[2] + CAMERA_HEIGHT_OFFSET,
        )
        
        direction = Vector((
            target_loc[0] - camera.location[0],
            target_loc[1] - camera.location[1],
            target_loc[2] - camera.location[2],
        ))
        
        track_quat = direction.to_track_quat("-Z", "Y")
        camera.rotation_euler = track_quat.to_euler()
        
        camera.keyframe_insert(data_path="location", frame=frame)
        camera.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    log(f"✓ Baked {(frame_end - frame_start) // FRAME_STEP + 1} keyframes", "SUCCESS")

def add_studio_lighting() -> None:
    """Add basic three-point lighting setup."""
    log("Adding studio lighting...")
    
    bpy.ops.object.light_add(type="AREA", location=(2, -2, 4))
    key_light = bpy.context.active_object
    key_light.name = "KeyLight"
    key_light.data.energy = 200
    key_light.data.size = 2
    
    bpy.ops.object.light_add(type="AREA", location=(-2, -1, 2))
    fill_light = bpy.context.active_object
    fill_light.name = "FillLight"
    fill_light.data.energy = 100
    fill_light.data.size = 2
    
    bpy.ops.object.light_add(type="SPOT", location=(0, 2, 3))
    rim_light = bpy.context.active_object
    rim_light.name = "RimLight"
    rim_light.data.energy = 150
    
    log("✓ Lighting setup complete", "SUCCESS")

def render_to_mp4(
    output_path: Path,
    fps: int = 24,
    quality: str = "high",
    frame_start: int = None,
    frame_end: int = None,
) -> Path:
    """Render animation to MP4 using GPU."""
    scene = bpy.context.scene
    
    if frame_start is None:
        frame_start = scene.frame_start
    if frame_end is None:
        frame_end = scene.frame_end
    
    log(f"Rendering frames {frame_start} to {frame_end} (GPU)...")
    
    original_media_type = scene.render.image_settings.media_type
    original_format = scene.render.image_settings.file_format
    original_filepath = scene.render.filepath
    original_start = scene.frame_start
    original_end = scene.frame_end
    
    try:
        scene.render.image_settings.media_type = 'VIDEO'
        scene.render.image_settings.file_format = 'FFMPEG'
        scene.render.ffmpeg.format = 'MPEG4'
        scene.render.ffmpeg.codec = 'H264'
        
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
        
        # Disable audio to avoid codec issues
        scene.render.ffmpeg.audio_codec = 'NONE'
        
        scene.render.fps = fps
        scene.render.fps_base = 1.0
        
        output_path = output_path.resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Ensure .mp4 extension
        if not str(output_path).endswith('.mp4'):
            output_path = output_path.with_suffix('.mp4')
        
        scene.render.filepath = str(output_path)
        scene.frame_start = frame_start
        scene.frame_end = frame_end
        
        log(f"Output: {scene.render.filepath}")
        log(f"Frame range: {frame_start} to {frame_end}")
        log(f"Resolution: {scene.render.resolution_x}x{scene.render.resolution_y} @ {scene.render.resolution_percentage}%")
        log(f"Engine: {scene.render.engine}")
        log(f"FFmpeg codec: {scene.render.ffmpeg.codec}")
        
        # Verify settings
        log(f"File format: {scene.render.image_settings.file_format}")
        log(f"Media type: {scene.render.image_settings.media_type}")
        
        # Log before rendering
        log("Initiating render...", "RENDER")
        
        try:
            # Attempt render
            result = bpy.ops.render.render(animation=True, write_still=False)
            log(f"Render operation completed with result: {result}", "SUCCESS")
        except RuntimeError as e:
            log(f"Runtime error during render: {e}", "ERROR")
            # Try with viewport as fallback  
            try:
                log("Attempting alternative render method...")
                bpy.ops.render.opengl(animation=True, write_still=False)
                log("Alternative render completed", "SUCCESS")
            except Exception as e2:
                log(f"Alternative render also failed: {e2}", "ERROR")
                raise
        
        log(f"✓ MP4 render operation finished", "SUCCESS")
        
        if output_path.exists():
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            log(f"  Size: {file_size_mb:.2f} MB")
            log(f"  Resolution: {scene.render.resolution_x}x{scene.render.resolution_y}")
            log(f"  Duration: {(frame_end - frame_start + 1) / fps:.2f}s")
        
    except Exception as e:
        log(f"Error during rendering: {e}", "ERROR")
        raise
    finally:
        scene.render.image_settings.media_type = original_media_type
        scene.render.image_settings.file_format = original_format
        scene.render.filepath = original_filepath
        scene.frame_start = original_start
        scene.frame_end = original_end
    
    return output_path

def remove_imported_objects(imported_objects: list) -> None:
    """Remove imported objects from the scene."""
    ensure_object_mode()
    for obj in imported_objects:
        if obj.name in bpy.data.objects:
            bpy.data.objects.remove(obj, do_unlink=True)

def main():
    """Main batch render function."""
    log("🎬 Batch Render with RadianceField", "HEADER")
    log("=" * 60)
    
    # Validate paths
    if not CHARACTERS_PATH.exists():
        log(f"Error: Characters folder not found: {CHARACTERS_PATH}", "ERROR")
        return
    
    if not POINTCLOUDS_PATH.exists():
        log(f"Error: Pointclouds folder not found: {POINTCLOUDS_PATH}", "ERROR")
        return
    
    if not RADIANCEFIELD_BLEND.exists():
        log(f"Error: radiancefield.blend not found: {RADIANCEFIELD_BLEND}", "ERROR")
        return
    
    # Collect FBX and PLY files in specified order
    fbx_order = ["doozy-hiphop.fbx", "vegas-hiphop.fbx", "michelle-hiphop.fbx", "mouse-hiphop.fbx"]
    fbx_files = [CHARACTERS_PATH / name for name in fbx_order if (CHARACTERS_PATH / name).exists()]
    
    # PLY files in specified order
    ply_order = [
        "Mailbox_point_cloud.ply",
        "Hydrant_vertical_point_cloud.ply",
        "David_Bust_point_cloud.ply",
        "McLaren_point_cloud.ply",
        "Panzernashorn_Tobler_point_cloud.ply"
    ]
    ply_files = [POINTCLOUDS_PATH / name for name in ply_order if (POINTCLOUDS_PATH / name).exists()]
    
    log(f"Found {len(fbx_files)} FBX files")
    for f in fbx_files:
        log(f"  - {f.name}")
    
    log(f"\nFound {len(ply_files)} PLY files")
    for f in ply_files:
        log(f"  - {f.name}")
    
    if not fbx_files:
        log("Error: No FBX files found", "ERROR")
        return
    
    if not ply_files:
        log("Error: No PLY files found", "ERROR")
        return
    
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    
    total_renders = len(fbx_files) * len(ply_files)
    current_render = 1
    
    # Process each FBX file with each PLY file
    for fbx_file in fbx_files:
        for ply_file in ply_files:
            log(f"\n[{current_render}/{total_renders}] {fbx_file.stem} + {ply_file.stem}", "RENDER")
            
            try:
                log("Resetting scene...")
                reset_scene()
                ensure_object_mode()
                
                pointcloud = import_ply_pointcloud(ply_file)
                apply_radiancefield(pointcloud, RADIANCEFIELD_BLEND)
                
                fbx_objects = import_fbx(fbx_file)
                
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
                    log("Warning: No armature found in FBX", "WARNING")
                    frame_end = 250
                    bpy.context.scene.frame_start = 1
                    bpy.context.scene.frame_end = frame_end
                    target = fbx_objects[0] if fbx_objects else None
                    target_bone = None
                
                log("Creating camera...")
                camera = create_tiktok_camera()
                
                if target:
                    setup_camera_tracking(camera, target, target_bone, 1, frame_end)
                
                add_studio_lighting()
                
                output_file = OUTPUT_PATH / f"{fbx_file.stem}_{ply_file.stem}.mp4"
                log(f"\nRendering to: {output_file}")
                render_to_mp4(output_file, fps=24, quality="high", frame_start=1, frame_end=frame_end)
                
                log(f"✓ Completed: {output_file.name}", "SUCCESS")
                
            except Exception as e:
                log(f"✗ Error rendering {fbx_file.stem} + {ply_file.stem}: {e}", "ERROR")
                continue
            
            finally:
                current_render += 1
    
    log("\n" + "=" * 60)
    log(f"✨ Batch rendering complete! All {total_renders} videos saved to: {OUTPUT_PATH}", "HEADER")

if __name__ == "__main__":
    main()
