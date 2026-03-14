#!/usr/bin/env python3
"""
Fast Batch Render Script: Low Quality PNG Frames
Renders 15 video combinations (4 FBX + 5 PLY) as PNG frame sequences
using low quality settings for fast rendering.
"""

from pathlib import Path
import bpy
from mathutils import Vector
import struct

CHARACTERS_PATH = Path(r"f:\研一\Tech Direction\tdspring26\tdspring26\characters")
POINTCLOUDS_PATH = Path(r"f:\研一\Tech Direction\tdspring26\tdspring26\pointclouds")
RADIANCEFIELD_BLEND = Path(r"f:\研一\Tech Direction\tdspring26\tdspring26\exercises\project2\radiancefield.blend")
OUTPUT_PATH = Path(r"f:\研一\Tech Direction\tdspring26\tdspring26\exercises\project2\videos")

FRAME_STEP = 5
CAMERA_DISTANCE = 2.5
CAMERA_HEIGHT_OFFSET = 1.5
TARGET_BONE_NAME = "mixamorig:Hips"

def log(message, level="INFO"):
    """Print log message."""
    print(f"[{level}] {message}")

def setup_gpu_rendering(quality="low"):
    """Configure GPU rendering with quality settings."""
    log(f"Setting up GPU rendering (Quality: {quality})...")
    
    try:
        bpy.context.scene.render.engine = "CYCLES"
        bpy.context.scene.cycles.use_denoising = True
        
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
    """Reset scene with low-quality settings for fast rendering."""
    log("Resetting scene...")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # Resolution reduced for faster rendering
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_y = 1920
    bpy.context.scene.render.resolution_percentage = 25  # 25% = 270x480 actual
    
    setup_gpu_rendering(quality)

def import_ply_file(ply_path):
    """Import PLY file."""
    log(f"Parsing PLY: {ply_path.name}")
    
    mesh = bpy.data.meshes.new("Pointcloud_Mesh")
    obj = bpy.data.objects.new("Pointcloud", mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
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
                continue
            
            header_lines.append(line_str)
            if line_str == 'end_header':
                break
        
        # Parse header
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
        
        log(f"  Verts: {vertex_count}, Faces: {face_count}")
        
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
        log(f"✓ PLY imported")
    
    return [obj]

def apply_radiancefield(pointcloud, radiancefield_blend):
    """Apply RadianceField node group."""
    log("Applying RadianceField...")
    
    with bpy.data.libraries.load(str(radiancefield_blend), link=False) as (data_from, data_to):
        if "RadianceField" in data_from.node_groups:
            data_to.node_groups.append("RadianceField")
            log("✓ RadianceField loaded")
        else:
            log("⚠ RadianceField not found", "WARNING")
            return
    
    if "RadianceField" in bpy.data.node_groups:
        radiancefield_group = bpy.data.node_groups["RadianceField"]
        mod = pointcloud.modifiers.new(name="GeometryNodes", type='NODES')
        mod.node_group = radiancefield_group
        log("✓ GeometryNodes applied")

def import_fbx(fbx_path):
    """Import FBX."""
    log(f"Importing FBX: {fbx_path.name}")
    objects_before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(fbx_path))
    objects_after = set(bpy.data.objects)
    imported_objects = list(objects_after - objects_before)
    log(f"✓ FBX imported")
    return imported_objects

def find_armature(objects):
    """Find armature."""
    for obj in objects:
        if obj.type == "ARMATURE":
            return obj
    return None

def get_target_world_location(armature, bone_name):
    """Get bone location."""
    if bone_name in armature.pose.bones:
        bone = armature.pose.bones[bone_name]
        matrix = armature.matrix_world @ bone.matrix
        return tuple(matrix.translation)
    return tuple(armature.matrix_world.translation)

def create_camera():
    """Create camera."""
    bpy.ops.object.camera_add()
    camera = bpy.context.active_object
    camera.name = "TikTokCamera"
    camera.data.lens = 50
    bpy.context.scene.camera = camera
    return camera

def setup_camera_tracking(camera, target, bone_name, frame_start, frame_end):
    """Setup camera tracking."""
    log(f"Setting up camera (frames {frame_start}-{frame_end})")
    
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

def add_lighting():
    """Add lights."""
    bpy.ops.object.light_add(type="AREA", location=(2, -2, 4))
    light = bpy.context.active_object
    light.data.energy = 200
    light.data.size = 2

def render_png_sequence(output_base_path, frame_start, frame_end):
    """Render animation as PNG frames."""
    log(f"Rendering frames {frame_start}-{frame_end} as PNG...")
    
    scene = bpy.context.scene
    
    frames_dir = output_base_path.parent / (output_base_path.stem + "_frames")
    frames_dir.mkdir(parents=True, exist_ok=True)
    
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = str(frames_dir / "frame_####.png")
    scene.frame_start = frame_start
    scene.frame_end = frame_end
    
    try:
        log(f"Frame output: {frames_dir}")
        bpy.ops.render.render(animation=True, write_still=False)
        
        png_files = sorted(list(frames_dir.glob("frame_*.png")))
        if png_files:
            log(f"✓ Rendered {len(png_files)} frames", "SUCCESS")
        else:
            log("✗ No frames created!", "ERROR")
        
        return output_base_path
        
    except Exception as e:
        log(f"Render error: {e}", "ERROR")
        raise

def main():
    """Main batch render."""
    log("=" * 70)
    log("FAST BATCH RENDER - LOW QUALITY PNG FRAMES", "HEADER")
    log("=" * 70)
    
    # File lists
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
    
    log(f"\nFBX files: {len(fbx_files)}")
    for f in fbx_files:
        log(f"  - {f.name}")
    
    log(f"\nPLY files: {len(ply_files)}")
    for f in ply_files:
        log(f"  - {f.name}")
    
    if not fbx_files or not ply_files:
        log("✗ Missing files!", "ERROR")
        return
    
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    
    total_renders = len(fbx_files) * len(ply_files)
    current_render = 1
    
    # Render each combination
    for fbx_file in fbx_files:
        for ply_file in ply_files:
            log("\n" + "=" * 70)
            log(f"[{current_render}/{total_renders}] {fbx_file.stem} + {ply_file.stem}", "RENDER")
            log("=" * 70)
            
            try:
                reset_scene(quality="low")
                
                # Import PLY
                import_ply_file(ply_file)
                pointcloud = bpy.context.active_object
                pointcloud.name = "Pointcloud"
                
                # Apply RadianceField
                apply_radiancefield(pointcloud, RADIANCEFIELD_BLEND)
                
                # Import FBX
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
                    log("⚠ No armature found", "WARNING")
                    frame_end = 250
                    target = fbx_objects[0] if fbx_objects else None
                    target_bone = None
                
                log(f"Animation: 1 to {frame_end} frames")
                
                # Camera & lighting
                camera = create_camera()
                if target:
                    setup_camera_tracking(camera, target, target_bone, 1, frame_end)
                add_lighting()
                
                # Render
                output_file = OUTPUT_PATH / f"{fbx_file.stem}_{ply_file.stem}"
                render_png_sequence(output_file, 1, frame_end)
                
                log(f"✓ COMPLETED: {fbx_file.stem}_{ply_file.stem}", "SUCCESS")
                
            except Exception as e:
                log(f"✗ ERROR: {e}", "ERROR")
                continue
            
            finally:
                current_render += 1
    
    log("\n" + "=" * 70)
    log(f"✓ BATCH RENDER COMPLETE! All {total_renders} PNG sequences saved", "HEADER")
    log(f"Output directory: {OUTPUT_PATH}")
    log("=" * 70)

if __name__ == "__main__":
    main()
