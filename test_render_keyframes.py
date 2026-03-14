#!/usr/bin/env python3
"""
Quick Test Render: Only First & Last Frames
Tests camera, pointcloud visibility, and RadianceField setup
Uses: doozy-hiphop.fbx + Mailbox_point_cloud.ply
"""

from pathlib import Path
import bpy
from mathutils import Vector
import struct
import time

CHARACTERS_PATH = Path(r"f:\研一\Tech Direction\tdspring26\tdspring26\characters")
POINTCLOUDS_PATH = Path(r"f:\研一\Tech Direction\tdspring26\tdspring26\pointclouds")
RADIANCEFIELD_BLEND = Path(r"f:\研一\Tech Direction\tdspring26\tdspring26\exercises\project2\radiancefield.blend")
OUTPUT_PATH = Path(r"f:\研一\Tech Direction\tdspring26\tdspring26\exercises\project2\test_frames")

FRAME_STEP = 5
CAMERA_DISTANCE = 5.5      # 增加距离以容纳整个角色和Pointcloud
CAMERA_HEIGHT_OFFSET = 1.2  # 相机高度
CAMERA_FOV = 45             # 减小FOV以获得更好的角色显示
TARGET_BONE_NAME = "mixamorig:Hips"
FPS = 24

def log(message, level="INFO"):
    """Print log message with timestamp."""
    import datetime
    time_str = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{time_str}] [{level}] {message}")

def setup_gpu_rendering(quality="low"):
    """Configure GPU rendering."""
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
        
        bpy.context.scene.cycles.samples = 32
        bpy.context.scene.cycles.use_denoising = True
        log(f"✓ Samples: 32")
        
    except Exception as e:
        log(f"GPU setup warning: {e}", "WARNING")

def reset_scene(quality="low"):
    """Reset scene."""
    log("Resetting scene...")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_y = 1920
    bpy.context.scene.render.resolution_percentage = 25
    
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
        if "RadianceField" in bpy.data.node_groups:
            bpy.data.node_groups.remove(bpy.data.node_groups["RadianceField"])
            log("  Cleared existing RadianceField")
        
        with bpy.data.libraries.load(str(radiancefield_blend), link=False) as (data_from, data_to):
            if "RadianceField" not in data_from.node_groups:
                log(f"✗ RadianceField not found in {radiancefield_blend.name}", "ERROR")
                return False
            
            data_to.node_groups.append("RadianceField")
            log("  ✓ RadianceField node group loaded")
        
        if "RadianceField" not in bpy.data.node_groups:
            log("✗ RadianceField loading verification failed", "ERROR")
            return False
        
        radiancefield_group = bpy.data.node_groups["RadianceField"]
        
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
    """Find armature."""
    for obj in objects:
        if obj.type == "ARMATURE":
            return obj
    return None

def get_character_bounds(armature):
    """Get character's bounding box to ensure it fits within pointcloud."""
    # Deselect all
    for obj in bpy.data.objects:
        obj.select_set(False)
    
    # Select armature and all children
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    
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
        return {
            'min': (0, 0, 0),
            'max': (0, 2, 0),
            'center': (0, 1, 0),
            'size': (0, 2, 0),
            'height': 2.0
        }
    
    height = max_z - min_z
    log(f"  Character bounds: min=({min_x:.2f}, {min_y:.2f}, {min_z:.2f}), max=({max_x:.2f}, {max_y:.2f}, {max_z:.2f})")
    log(f"  Character size: ({max_x - min_x:.2f}, {max_y - min_y:.2f}, {height:.2f})")
    
    return {
        'min': (min_x, min_y, min_z),
        'max': (max_x, max_y, max_z),
        'center': ((min_x + max_x) / 2, (min_y + max_y) / 2, (min_z + max_z) / 2),
        'size': (max_x - min_x, max_y - min_y, height),
        'height': height
    }

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
    camera.data.lens = CAMERA_FOV
    camera.data.sensor_width = 36
    bpy.context.scene.camera = camera
    log(f"✓ Camera created (FOV: {CAMERA_FOV}°)")
    return camera

def setup_camera_tracking(camera, target, bone_name, frame_start, frame_end, pc_center):
    """Setup camera tracking with full character visibility."""
    log(f"Setting up camera tracking (frames {frame_start} & {frame_end})")
    
    if camera.animation_data:
        camera.animation_data_clear()
    
    scene = bpy.context.scene
    
    # Keyframes for first and last frames only
    for frame in [frame_start, frame_end]:
        scene.frame_set(frame)
        
        if target.type == "ARMATURE" and bone_name:
            target_loc = get_target_world_location(target, bone_name)
        else:
            target_loc = tuple(target.matrix_world.translation)
        
        # Position camera around the pointcloud center
        # Use pc_center for reference instead of target_loc
        camera.location = (
            pc_center[0] + 1.5,       # Slightly to the right
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

def add_lighting():
    """Add lights."""
    bpy.ops.object.light_add(type="AREA", location=(3, -3, 3))
    light1 = bpy.context.active_object
    light1.data.energy = 300
    light1.data.size = 3
    
    bpy.ops.object.light_add(type="AREA", location=(-2, 2, 2))
    light2 = bpy.context.active_object
    light2.data.energy = 100
    light2.data.size = 2
    
    log("✓ Lighting setup complete")

def verify_scene_visibility():
    """Verify visibility and report object positions."""
    log("Verifying scene visibility...")
    
    camera = bpy.context.scene.camera
    if not camera:
        log("⚠ No camera found", "WARNING")
        return False
    
    scene = bpy.context.scene
    
    # Check character
    armature = None
    for obj in scene.objects:
        if obj.type == "ARMATURE":
            armature = obj
            break
    
    if not armature:
        log("⚠ No character/armature found", "WARNING")
    else:
        log(f"✓ Character at {tuple(armature.location)[:3]}")
    
    # Check pointcloud
    pointcloud = bpy.data.objects.get("Pointcloud")
    if not pointcloud:
        log("⚠ Pointcloud not found", "WARNING")
        return False
    
    if pointcloud.hide_viewport or pointcloud.hide_render:
        pointcloud.hide_viewport = False
        pointcloud.hide_render = False
        log("  Fixed hidden pointcloud visibility")
    
    # Get pointcloud info
    bbox = pointcloud.bound_box
    bounds_min = tuple(bbox[0])
    bounds_max = tuple(bbox[6])
    pc_center = tuple((bounds_min[i] + bounds_max[i]) / 2 for i in range(3))
    pc_size = tuple(bounds_max[i] - bounds_min[i] for i in range(3))
    log(f"✓ Pointcloud at {tuple(pointcloud.location)}, size: {pc_size}")
    
    # Report camera
    log(f"✓ Camera at {tuple(camera.location)[:3]}")
    
    return True

def render_keyframes(output_dir, frame_start, frame_end):
    """Render only first and last frames."""
    log(f"Rendering keyframes {frame_start} and {frame_end}...")
    
    scene = bpy.context.scene
    output_dir.mkdir(parents=True, exist_ok=True)
    
    scene.render.image_settings.file_format = 'PNG'
    scene.frame_start = frame_start
    scene.frame_end = frame_end
    
    try:
        # Render frame 1
        log(f"Rendering frame {frame_start}...")
        scene.frame_set(frame_start)
        scene.render.filepath = str(output_dir / f"frame_{frame_start:04d}.png")
        bpy.ops.render.render(write_still=True)
        
        # Render last frame
        log(f"Rendering frame {frame_end}...")
        scene.frame_set(frame_end)
        scene.render.filepath = str(output_dir / f"frame_{frame_end:04d}.png")
        bpy.ops.render.render(write_still=True)
        
        png_files = sorted(list(output_dir.glob("frame_*.png")))
        if png_files:
            log(f"✓ Rendered {len(png_files)} keyframes")
            for f in png_files:
                size_kb = f.stat().st_size / 1024
                log(f"  {f.name} ({size_kb:.1f} KB)")
            return True
        else:
            log("✗ No frames created", "ERROR")
            return False
        
    except Exception as e:
        log(f"Render error: {e}", "ERROR")
        return False

def main():
    """Main test render."""
    log("=" * 80)
    log("TEST RENDER - KEYFRAMES ONLY (First & Last Frames)", "HEADER")
    log("=" * 80)
    
    fbx_file = CHARACTERS_PATH / "doozy-hiphop.fbx"
    ply_file = POINTCLOUDS_PATH / "Mailbox_point_cloud.ply"
    
    if not fbx_file.exists():
        log(f"✗ FBX not found: {fbx_file}", "ERROR")
        return
    
    if not ply_file.exists():
        log(f"✗ PLY not found: {ply_file}", "ERROR")
        return
    
    log(f"\nTest Configuration:")
    log(f"  FBX: {fbx_file.name}")
    log(f"  PLY: {ply_file.name}")
    
    start_time = time.time()
    
    try:
        reset_scene(quality="low")
        
        # Import PLY first (to get its center)
        pointcloud = import_ply_file(ply_file)
        pointcloud.name = "Pointcloud"
        
        # Setup Pointcloud: rotate 90° and align to origin
        setup_pointcloud(pointcloud)
        
        # Import FBX
        fbx_objects = import_fbx(fbx_file)
        armature = find_armature(fbx_objects)
        
        # Get character bounds
        if armature:
            log("Analyzing character bounds...")
            char_bounds = get_character_bounds(armature)
            char_height = char_bounds['height']
            
            # Pointcloud bounds (after 90° rotation): X±2, Y±2, Z±5
            # Position character so it's centered Z-wise within pointcloud
            pc_height = 10.0  # Pointcloud Z height
            z_center = (pc_height - char_height) / 2 - 5.0  # Position so char fits in middle
            
            # Final position: centered in XY, positioned in Z to fit within pointcloud
            armature.location = (0, 0, z_center)
            log(f"✓ Armature positioned within pointcloud: (0, 0, {z_center:.2f})")
            log(f"  Character will span Z: {z_center - char_height/2:.2f} to {z_center + char_height/2:.2f}")
        
        # Get actual pc_center (at origin for this setup)
        pc_center = (0, 0, 0)
        
        # Apply RadianceField
        if not apply_radiancefield(pointcloud, RADIANCEFIELD_BLEND):
            log(f"✗ Failed to apply RadianceField", "ERROR")
            return
        
        # Setup frame range
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
            frame_end = 250
            target = fbx_objects[0] if fbx_objects else None
            target_bone = None
        
        log(f"Animation frame range: 1 to {frame_end}")
        
        # Camera & lighting
        camera = create_camera()
        if target:
            setup_camera_tracking(camera, target, target_bone, 1, frame_end, pc_center)
        add_lighting()
        
        # Verify visibility
        if not verify_scene_visibility():
            log("⚠ Scene visibility check failed, but continuing", "WARNING")
        
        # Render keyframes
        output_dir = OUTPUT_PATH / "test_keyframes"
        if not render_keyframes(output_dir, 1, frame_end):
            return
        
        elapsed = int(time.time() - start_time)
        log("")
        log("=" * 80)
        log(f"✓ TEST RENDER COMPLETE", "HEADER")
        log(f"  Frames: {output_dir}")
        log(f"  Time: {elapsed}s")
        log("=" * 80)
        
    except Exception as e:
        log(f"✗ Error: {e}", "ERROR")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
