import struct
import json
import os

def create_placeholder_glb(filename):
    """Create a minimal valid GLB file (placeholder)"""
    
    # Minimal glTF JSON scene with a cube
    gltf_json = {
        "asset": {"version": "2.0"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0}],
        "meshes": [{
            "primitives": [{
                "attributes": {"POSITION": 0},
                "indices": 1,
                "material": 0
            }]
        }],
        "materials": [{
            "pbrMetallicRoughness": {"baseColorFactor": [0.8, 0.8, 0.8, 1.0]}
        }],
        "accessors": [
            {
                "bufferView": 0,
                "componentType": 5126,
                "count": 24,
                "type": "VEC3"
            },
            {
                "bufferView": 1,
                "componentType": 5125,
                "count": 36,
                "type": "SCALAR"
            }
        ],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteStride": 12},
            {"buffer": 0, "byteOffset": 288}
        ],
        "buffers": [{"byteLength": 432}]
    }
    
    # Create vertex data for a cube
    vertices = [
        -1, -1, -1,   1, -1, -1,   1,  1, -1,  -1,  1, -1,  # Back
        -1, -1,  1,   1, -1,  1,   1,  1,  1,  -1,  1,  1,  # Front
    ]
    vertices = struct.pack('<' + 'f' * len(vertices), *vertices)
    
    # Index data for cube faces
    indices = [
        0, 1, 2, 2, 3, 0,  # Back
        4, 6, 5, 4, 7, 6,  # Front
        0, 4, 5, 5, 1, 0,  # Bottom
        2, 6, 7, 7, 3, 2,  # Top
        0, 3, 7, 7, 4, 0,  # Left
        1, 5, 6, 6, 2, 1,  # Right
    ]
    indices = struct.pack('<' + 'I' * len(indices), *indices)
    
    # Combine binary data
    binary_data = vertices + indices
    
    # Convert JSON to binary
    json_str = json.dumps(gltf_json)
    json_bytes = json_str.encode('utf-8')
    
    # Pad JSON to 4-byte boundary
    json_padding = (4 - len(json_bytes) % 4) % 4
    json_bytes += b' ' * json_padding
    
    # GLB header
    glb = bytearray()
    glb += struct.pack('<I', 0x46546C67)  # "glTF"
    glb += struct.pack('<I', 2)           # Version
    glb += struct.pack('<I', 28 + len(json_bytes) + len(binary_data) + 8 + 8)  # Total size
    
    # JSON chunk
    glb += struct.pack('<I', len(json_bytes))
    glb += struct.pack('<I', 0x4E4F534A)  # "JSON"
    glb += json_bytes
    
    # Binary chunk
    glb += struct.pack('<I', len(binary_data))
    glb += struct.pack('<I', 0x004E4942)  # "BIN\0"
    glb += binary_data
    
    # Write file
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'wb') as f:
        f.write(glb)
    print(f"✓ Created placeholder: {filename}")

# Create placeholder GLB files
models = {
    "f:\\研一\\Tech Direction\\tdspring26\\tdspring26\\public\\models\\teddy\\Bear O.glb": "Teddy Bear (Placeholder)",
    "f:\\研一\\Tech Direction\\tdspring26\\tdspring26\\public\\models\\monsters\\Bear S.glb": "Monster 1 (Placeholder)",
    "f:\\研一\\Tech Direction\\tdspring26\\tdspring26\\public\\models\\monsters\\人台.glb": "Monster 2 (Placeholder)",
    "f:\\研一\\Tech Direction\\tdspring26\\tdspring26\\public\\models\\monsters\\蜉蝣.glb": "Monster 3 (Placeholder)",
}

print("Creating placeholder GLB files...")
print("=" * 60)
for path, name in models.items():
    create_placeholder_glb(path)
    print(f"  {name}")
print("=" * 60)
print("\n✓ Placeholder models created!")
print("\nNow you can run: npm run dev")
print("Replace these placeholder models by converting your FBX files")
print("See public/models/README.md for conversion instructions")
