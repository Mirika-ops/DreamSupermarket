# 🎨 Model Conversion Instructions

Your FBX models have been placed in the `public/models/` folder:

```
public/models/
├── teddy/
│   └── Bear O.fbx
└── monsters/
    ├── Bear S.fbx
    ├── 人台.fbx
    └── 蜉蝣.fbx
```

## Converting FBX to GLB

Three.js requires GLB/GLTF format. You can convert using Blender:

### Option 1: Using the Conversion Script (Recommended)
If Blender is installed on your system:

```bash
blender --background --python convert_fbx_to_glb.py
```

This will automatically convert all FBX files in public/models/ to GLB format.

### Option 2: Manual Blender Conversion
1. Open Blender
2. File → Import → FBX (.fbx)
3. Select your FBX file from `public/models/`
4. File → Export As → glTF 2.0 (.glb/.gltf)
5. Save in the same folder with same name

### Converted Files Will Be:
- `public/models/teddy/Bear O.glb`
- `public/models/monsters/Bear S.glb`
- `public/models/monsters/人台.glb`
- `public/models/monsters/蜉蝣.glb`

## Quick Rename (If Needed)

If you want simpler filenames, rename them to:
- `public/models/teddy/modelA.glb`
- `public/models/monsters/monster01.glb`
- `public/models/monsters/monster02.glb`
- `public/models/monsters/monster03.glb`

Then update `sceneConfig.ts` to match the new names.
