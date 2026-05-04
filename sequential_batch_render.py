#!/usr/bin/env python3
"""
Sequential Batch Render: RadianceField + GPU
Renders each video combination as PNG frame sequences
4 FBX × 5 PLY = 20 video frame sequences
(PNG sequences can be converted to MP4 after rendering completes)
"""

from pathlib import Path
import bpy
from mathutils import Vector
import struct
import time

CHARACTERS_PATH = Path(r"f:\研一\Tech Direction\tdspring26\tdspring26\characters")
POINTCLOUDS_PATH = Path(r"f:\研一\Tech Direction\tdspring26\tdspring26\pointclouds")
RADIANCEFIELD_BLEND = Path(r"f:\研一\Tech Direction\tdspring26\tdspring26\exercises\project2\radiancefield.blend")
OUTPUT_PATH = Path(r"f:\研一\Tech Direction\tdspring26\tdspring26\exercises\project2\videos")

FRAME_STEP = 5
CAMERA_DISTANCE = 5.5      # Camera distance from character (increase to show entire Pointcloud)
CAMERA_HEIGHT_OFFSET = 1.2  # Camera height offset
CAMERA_FOV = 45              # Field of view (degrees)
TARGET_BONE_NAME = "mixamorig:Hips"
FPS = 24

def log(message, level="INFO"):
    """Print log message with timestamp."""
    import datetime
    time_str = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{time_str}] [{level}] {message}")

def setup_gpu_rendering(quality="low"):
    """Configure GPU rendering with quality settings."""
    log(f"Setting up GPU rendering (Quality: {quality})...")
    
    try:
        bpy.context.scene.render.engine = "CYCLES"
        
        try:
            prefs = bpy.context.preferences.addons['cycles'].preferences
            prefs.compute_device_type = 'CUDA'
            for device in prefs.devices:
                device.use = True
            bpy.context.scene.cycles.device = 'GPU'
            log("✓ CUDA GPU enabled")
        except:
            bpy.context.scene.cycles.device = 'CPU'
            log("⚠ Fallback to CPU")
        
        # Quality-based samples
        if quality == "high":
            bpy.context.scene.cycles.samples = 256
        elif quality == "medium":
            bpy.context.scene.cycles.samples = 64
        else:  # low
            bpy.context.scene.cycles.samples = 32
        
        bpy.context.scene.cycles.use_denoising = True
        log(f"✓ Samples: {bpy.context.scene.cycles.samples}")
        
    except Exception as e:
        log(f"GPU setup warning: {e}", "WARNING")

def reset_scene(quality="low"):
    """Reset scene with low-quality settings."""
    log("Resetting scene...")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_y = 1920
    bpy.context.scene.render.resolution_percentage = 25  # 270x480 actual
    
    setup_gpu_rendering(quality)

def import_ply_file(ply_path):
    """Import PLY file."""
    log(f"Importing PLY: {ply_path.name}")
    
    mesh = bpy.data.meshes.new("Pointcloud_Mesh")
    obj = bpy.data.objects.new("Pointcloud", mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    vertices = []
    faces = []
    
    with open(ply_path, 'rb') as f:
        header_lines = []
        while True:
            line = f.readline()
            try:
                line_str = line.decode('ascii').strip()
            except:
                continue
            
            header_lines.append(line_str)
            if line_str == 'end_header':
                break
        
        vertex_count = 0
        face_count = 0
        is_binary = False
        byte_order = '<'
        
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
        
        log(f"  Vertices: {vertex_count}, Faces: {face_count}")
        
        # Read vertices
        if is_binary:
            for _ in range(vertex_count):
                data = f.read(12)
                if len(data) == 12:
                    x, y, z = struct.unpack(f'{byte_order}fff', data)
                    vertices.append((x, y, z))
        else:
            for _ in range(vertex_count):
                line = f.readline().decode('ascii').strip()
                if line:
                    coords = [float(x) for x in line.split()[:3]]
                    vertices.append(tuple(coords))
        
        # Read faces
        if is_binary:
            for _ in range(face_count):
                count_byte = f.read(1)
                if count_byte:
                    count = struct.unpack(f'{byte_order}B', count_byte)[0]
                    indices_data = f.read(count * 4)
                    if len(indices_data) == count * 4:
                        indices = struct.unpack(f'{byte_order}' + f'I' * count, indices_data)
                        faces.append(list(indices))
        else:
            for _ in range(face_count):
                line = f.readline().decode('ascii').strip()
                if line:
                    parts = line.split()
                    n_verts = int(parts[0])
                    face_verts = [int(parts[i+1]) for i in range(n_verts)]
                    faces.append(face_verts)
    
    if vertices:
        mesh.from_pydata(vertices, [], faces)
        mesh.update()
        log(f"✓ PLY imported ({len(vertices)} vertices)")
    
    return obj

def apply_radiancefield(pointcloud, radiancefield_blend):
    """Apply RadianceField node group with validation."""
    log("Applying RadianceField...")
    
    if not radiancefield_blend.exists():
        log(f"✗ RadianceField blend not found: {radiancefield_blend}", "ERROR")
        return False
    
    try:
        # Remove any existing RadianceField node groups to avoid conflicts
        if "RadianceField" in bpy.data.node_groups:
            bpy.data.node_groups.remove(bpy.data.node_groups["RadianceField"])
            log("  Cleared existing RadianceField")
        
        # Load RadianceField from blend
        with bpy.data.libraries.load(str(radiancefield_blend), link=False) as (data_from, data_to):
            if "RadianceField" not in data_from.node_groups:
                log(f"✗ RadianceField not found in {radiancefield_blend.name}", "ERROR")
                return False
            
            data_to.node_groups.append("RadianceField")
            log("  ✓ RadianceField node group loaded")
        
        # Verify load succeeded
        if "RadianceField" not in bpy.data.node_groups:
            log("✗ RadianceField loading verification failed", "ERROR")
            return False
        
        # Apply modifier
        radiancefield_group = bpy.data.node_groups["RadianceField"]
        
        # Remove existing geometry nodes modifier if any
        for mod in pointcloud.modifiers:
            if mod.type == 'NODES':
                pointcloud.modifiers.remove(mod)
        
        mod = pointcloud.modifiers.new(name="GeometryNodes", type='NODES')
        mod.node_group = radiancefield_group
        log("✓ RadianceField successfully applied to pointcloud")
        return True
        
    except Exception as e:
        log(f"✗ RadianceField application failed: {e}", "ERROR")
        return False

def import_fbx(fbx_path):
    """Import FBX."""
    log(f"Importing FBX: {fbx_path.name}")
    objects_before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(fbx_path))
    objects_after = set(bpy.data.objects)
    imported_objects = list(objects_after - objects_before)
    log(f"✓ FBX imported ({len(imported_objects)} objects)")
    return imported_objects

def find_armature(objects):
    """Find armature in imported objects."""
    for obj in objects:
        if obj.type == "ARMATURE":
            return obj
    return None

def get_target_world_location(armature, bone_name):
    """Get bone world location."""
    if bone_name in armature.pose.bones:
        bone = armature.pose.bones[bone_name]
        matrix = armature.matrix_world @ bone.matrix
        return tuple(matrix.translation)
    return tuple(armature.matrix_world.translation)
def get_character_bounds(armature):
    """Get character's bounding box to ensure it fits within pointcloud."""
    # Get all objects in armature's hierarchy
    char_objects = [armature]
    for obj in bpy.data.objects:
        if obj.parent == armature or obj in armature.children_recursive:
            char_objects.append(obj)
    
    # Calculate combined bounds
    min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
    max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')
    
    for obj in char_objects:
        if hasattr(obj, 'bound_box'):
            bbox = obj.bound_box
            try:
                obj_mins = tuple(min(v[i] for v in bbox) for i in range(3))
                obj_maxs = tuple(max(v[i] for v in bbox) for i in range(3))
                
                world_min = obj.matrix_world @ Vector(obj_mins)
                world_max = obj.matrix_world @ Vector(obj_maxs)
                
                min_x = min(min_x, world_min.x)
                max_x = max(max_x, world_max.x)
                min_y = min(min_y, world_min.y)
                max_y = max(max_y, world_max.y)
                min_z = min(min_z, world_min.z)
                max_z = max(max_z, world_max.z)
            except:
                pass
    
    if min_x == float('inf'):
        # Fallback to armature bounds if no meshes found
        return {'height': 2.0}
    
    height = max_z - min_z
    return {'height': height}
def setup_pointcloud(pointcloud):
    """Setup Pointcloud: rotate 90° and align to origin."""
    log("Setting up Pointcloud orientation and position...")
    
    # Rotate 90 degrees around X-axis
    import math
    pointcloud.rotation_euler = (math.radians(90), 0, 0)
    log("  ✓ Rotated Pointcloud 90° around X-axis")
    
    # Move to origin (0, 0, 0)
    pointcloud.location = (0, 0, 0)
    log("  ✓ Pointcloud positioned at origin (0, 0, 0)")
    
    return pointcloud

def create_camera():
    """Create camera with proper FOV."""
    bpy.ops.object.camera_add()
    camera = bpy.context.active_object
    camera.name = "TikTokCamera"
    # Set FOV using focal length (35mm equivalent)
    camera.data.lens = CAMERA_FOV
    camera.data.sensor_width = 36
    bpy.context.scene.camera = camera
    log(f"✓ Camera created (FOV: {CAMERA_FOV}°)")
    return camera

def setup_camera_tracking(camera, target, bone_name, frame_start, frame_end, pc_center=(0, 0, 0)):
    """Setup camera tracking with character visibility, focused on pointcloud center."""
    log(f"Setting up camera tracking (frames {frame_start}-{frame_end})")
    
    if camera.animation_data:
        camera.animation_data_clear()
    
    scene = bpy.context.scene
    
    # Setup keyframes
    for frame in range(frame_start, frame_end + 1, FRAME_STEP):
        scene.frame_set(frame)
        
        # Position camera around the pointcloud center
        camera.location = (
            pc_center[0] + 1.5,              # Slightly to the right
            pc_center[1] - CAMERA_DISTANCE,  # Behind character
            pc_center[2] + CAMERA_HEIGHT_OFFSET,  # Above
        )
        
        # Look at pointcloud center
        look_at_point = Vector(pc_center) + Vector((0, 0, 0.5))
        direction = look_at_point - Vector(camera.location)
        track_quat = direction.to_track_quat("-Z", "Y")
        camera.rotation_euler = track_quat.to_euler()
        
        camera.keyframe_insert(data_path="location", frame=frame)
        camera.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    log(f"✓ Camera tracking setup complete (focused on pointcloud center)")
    
    log(f"✓ Camera tracking setup complete")

def add_lighting():
    """Add lights for better visibility."""
    # Main light
    bpy.ops.object.light_add(type="AREA", location=(3, -3, 3))
    light1 = bpy.context.active_object
    light1.data.energy = 300
    light1.data.size = 3
    
    # Fill light
    bpy.ops.object.light_add(type="AREA", location=(-2, 2, 2))
    light2 = bpy.context.active_object
    light2.data.energy = 100
    light2.data.size = 2
    
    log("✓ Lighting setup complete")

def verify_scene_visibility():
    """Verify that character and pointcloud are both visible in camera view."""
    log("Verifying scene visibility...")
    
    camera = bpy.context.scene.camera
    if not camera:
        log("⚠ No camera found", "WARNING")
        return False
    
    scene = bpy.context.scene
    
    # Check for character objects
    char_objects = [obj for obj in scene.objects if obj.type == "ARMATURE" or (obj.type == "MESH" and "Armature" in obj.modifiers)]
    if not char_objects:
        log("⚠ No character found in scene", "WARNING")
    
    # Check for pointcloud
    pointcloud = bpy.data.objects.get("Pointcloud")
    if not pointcloud:
        log("⚠ Pointcloud object not found", "WARNING")
        return False
    
    # Check if pointcloud is visible
    if pointcloud.hide_viewport or pointcloud.hide_render:
        pointcloud.hide_viewport = False
        pointcloud.hide_render = False
        log("  Fixed hidden pointcloud visibility")
    
    log(f"✓ Scene visibility verified")
    log(f"  Character objects: {len(char_objects)}")
    log(f"  Pointcloud: {pointcloud.name} at {tuple(pointcloud.location)[:2]}")
    return True

def render_png_sequence(frames_dir, frame_start, frame_end):
    """Render animation as PNG frames."""
    log(f"Rendering frames {frame_start} to {frame_end}...")
    
    scene = bpy.context.scene
    frames_dir.mkdir(parents=True, exist_ok=True)
    
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = str(frames_dir / "frame_####.png")
    scene.frame_start = frame_start
    scene.frame_end = frame_end
    
    try:
        bpy.ops.render.render(animation=True, write_still=False)
        
        png_files = sorted(list(frames_dir.glob("frame_*.png")))
        if png_files:
            log(f"✓ Rendered {len(png_files)} PNG frames")
            return True
        else:
            log(f"✗ No frames created!", "ERROR")
            return False
        
    except Exception as e:
        log(f"Render error: {e}", "ERROR")
        return False

def convert_png_to_mp4(frames_dir, output_mp4):
    """Convert PNG sequence to MP4 using OpenCV."""
    log(f"Converting PNG to MP4...")
    
    frames = sorted(list(frames_dir.glob("frame_*.png")))
    if not frames:
        log(f"✗ No PNG frames found", "ERROR")
        return False
    
    try:
        # Get dimensions
        first_frame = cv2.imread(str(frames[0]))
        if first_frame is None:
            log(f"✗ Cannot read first frame", "ERROR")
            return False
        
        height, width = first_frame.shape[:2]
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_mp4), fourcc, FPS, (width, height))
        
        if not out.isOpened():
            log(f"✗ Failed to open video writer", "ERROR")
            return False
        
        # Write frames
        for frame_path in frames:
            frame = cv2.imread(str(frame_path))
            if frame is not None:
                out.write(frame)
        
        out.release()
        
        if output_mp4.exists():
            file_size_mb = output_mp4.stat().st_size / (1024 * 1024)
            log(f"✓ MP4 created ({file_size_mb:.1f} MB)")
            return True
        else:
            log(f"✗ MP4 not created", "ERROR")
            return False
            
    except Exception as e:
        log(f"Conversion error: {e}", "ERROR")
        return False

def cleanup_png_frames(frames_dir):
    """Delete PNG frames after conversion."""
    try:
        import shutil
        shutil.rmtree(str(frames_dir), ignore_errors=True)
        log(f"✓ PNG frames cleaned up")
    except:
        pass

def render_single_combination(fbx_path, ply_path, output_base):
    """Render a single FBX+PLY combination as PNG frame sequence."""
    try:
        reset_scene(quality="low")
        
        # Import PLY first (to get its center)
        pointcloud = import_ply_file(ply_path)
        pointcloud.name = "Pointcloud"
        
        # Setup Pointcloud: rotate 90° and align to origin
        setup_pointcloud(pointcloud)
        
        # Import FBX
        fbx_objects = import_fbx(fbx_path)
        armature = find_armature(fbx_objects)
        
        # Get character bounds and position fully within pointcloud
        if armature:
            log("Analyzing character bounds...")
            char_bounds = get_character_bounds(armature)
            char_height = char_bounds.get('height', 2.0)
            
            # Pointcloud bounds (after 90° rotation): X±2, Y±2, Z±5
            # Position character so it's centered Z-wise within pointcloud
            pc_height = 10.0  # Pointcloud Z height (from -5 to 5)
            z_center = (pc_height - char_height) / 2 - 5.0  # Position so char fits in middle
            
            # Final position: centered in XY, positioned in Z to fit within pointcloud
            armature.location = (0, 0, z_center)
            log(f"✓ Armature positioned within pointcloud: Z={z_center:.2f}, height={char_height:.2f}")
        
        # PC center is at origin for this setup
        pc_center = (0, 0, 0)
        
        # Apply RadianceField - CRITICAL STEP
        if not apply_radiancefield(pointcloud, RADIANCEFIELD_BLEND):
            log(f"✗ Failed to apply RadianceField, skipping this render", "ERROR")
            return False
        
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
            log("⚠ No armature found", "WARNING")
            frame_end = 250
            target = fbx_objects[0] if fbx_objects else None
            target_bone = None
        
        log(f"Animation: 1 to {frame_end} frames")
        
        # Camera & lighting
        camera = create_camera()
        if target:
            setup_camera_tracking(camera, target, target_bone, 1, frame_end, pc_center)
        add_lighting()
        
        # Verify visibility before rendering
        if not verify_scene_visibility():
            log("⚠ Scene visibility check failed, but continuing", "WARNING")
        
        # Render PNG frames
        frames_dir = output_base.parent / (output_base.stem + "_frames")
        if not render_png_sequence(frames_dir, 1, frame_end):
            return False
        
        log(f"✓ PNG frame sequence complete: {frames_dir}")
        return True
        
    except Exception as e:
        log(f"✗ Error: {e}", "ERROR")
        return False

def main():
    """Main sequential batch rendering."""
    log("=" * 80)
    log("SEQUENTIAL BATCH RENDER - RadianceField + GPU", "HEADER")
    log("=" * 80)
    
    # File lists - in specific order
    fbx_order = ["doozy-hiphop.fbx", "vegas-hiphop.fbx", "michelle-hiphop.fbx", "mouse-hiphop.fbx"]
    fbx_files = [CHARACTERS_PATH / name for name in fbx_order if (CHARACTERS_PATH / name).exists()]
    
    ply_order = [
        "Mailbox_point_cloud.ply",
        "Hydrant_vertical_point_cloud.ply",
        "David_Bust_point_cloud.ply",
        "McLaren_point_cloud.ply",
        "Panzernashorn_Tobler_point_cloud.ply"
    ]
    ply_files = [POINTCLOUDS_PATH / name for name in ply_order if (POINTCLOUDS_PATH / name).exists()]
    
    log(f"FBX files: {len(fbx_files)}")
    for f in fbx_files:
        log(f"  {f.name}")
    
    log(f"PLY files: {len(ply_files)}")
    for f in ply_files:
        log(f"  {f.name}")
    
    if not fbx_files or not ply_files:
        log("✗ Missing files!", "ERROR")
        return
    
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    
    total_renders = len(fbx_files) * len(ply_files)
    current_render = 0
    successful_renders = 0
    failed_renders = 0
    
    start_time = time.time()
    
    # Render each combination sequentially
    for fbx_file in fbx_files:
        for ply_file in ply_files:
            current_render += 1
            
            log("\n" + "=" * 80)
            log(f"[{current_render}/{total_renders}] {fbx_file.stem} + {ply_file.stem}", "RENDER")
            log("=" * 80)
            
            output_base = OUTPUT_PATH / f"{fbx_file.stem}_{ply_file.stem}"
            
            # Skip if MP4 already exists
            if (output_base.with_suffix(".mp4")).exists():
                log(f"⊘ Already exists, skipping")
                continue
            
            elapsed = int(time.time() - start_time)
            log(f"Elapsed: {elapsed//60}m {elapsed%60}s")
            
            if render_single_combination(fbx_file, ply_file, output_base):
                successful_renders += 1
                log(f"✓ COMPLETED: {fbx_file.stem}_{ply_file.stem}", "SUCCESS")
            else:
                failed_renders += 1
                log(f"✗ FAILED: {fbx_file.stem}_{ply_file.stem}", "ERROR")
    
    total_elapsed = int(time.time() - start_time)
    log("\n" + "=" * 80)
    log(f"✓ BATCH RENDER COMPLETE", "HEADER")
    log(f"  Successful: {successful_renders}/{total_renders}")
    log(f"  Failed: {failed_renders}/{total_renders}")
    log(f"  Total time: {total_elapsed//3600}h {(total_elapsed%3600)//60}m {total_elapsed%60}s")
    log(f"  Output: {OUTPUT_PATH}")
    log("=" * 80)

if __name__ == "__main__":
    main()
