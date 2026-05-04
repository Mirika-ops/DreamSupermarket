# Asset Folder Setup - Step by Step Guide

## 📁 Visual Directory Structure

Here's what your final folder structure should look like:

```
your-nextjs-project/
│
├── app/
│   ├── ParticleFieldVanilla.tsx     ← Your main scene component (UPDATED)
│   ├── page.tsx
│   ├── layout.tsx
│   └── globals.css
│
├── public/                          ← Asset location
│   ├── models/                      ← Create this folder
│   │   ├── teddy/                   ← Create this folder
│   │   │   └── modelA.glb           ← YOUR TEDDY BEAR MODEL
│   │   │
│   │   └── monsters/                ← Create this folder
│   │       ├── monster01.glb        ← Random monster 1
│   │       ├── monster02.glb        ← Random monster 2
│   │       └── monster03.glb        ← Random monster 3
│   │                                (Add more as needed)
│   │
│   └── (other assets)
│
├── sceneConfig.ts                   ← Configuration (CREATED)
├── types.ts                         ← Type definitions (CREATED)
│
├── IMPLEMENTATION_SUMMARY.md        ← Main documentation (CREATED)
├── QUICK_START.md                   ← Quick reference (CREATED)
├── EXHIBITION_SCENE_README.md       ← Detailed guide (CREATED)
├── ARCHITECTURE.md                  ← System design (CREATED)
├── CONFIG_CHEATSHEET.md             ← Config reference (CREATED)
├── VERIFICATION_CHECKLIST.md        ← Testing guide (CREATED)
│
├── package.json
├── tsconfig.json
├── next.config.ts
└── (other files)
```

---

## 🚀 Setup Steps (Detailed)

### Step 1: Create Folder Structure

#### Windows (Command Prompt or PowerShell):
```powershell
# Navigate to project root
cd "path\to\your\nextjs\project"

# Create model folders
mkdir public\models
mkdir public\models\teddy
mkdir public\models\monsters

# Verify folders created
dir public\models
```

#### Mac/Linux (Terminal):
```bash
# Navigate to project root
cd path/to/your/nextjs/project

# Create model folders
mkdir -p public/models/teddy
mkdir -p public/models/monsters

# Verify folders created
ls -la public/models/
```

### Step 2: Place Your GLTF Files

You should have these files:
- Your teddy bear model (any name ending in `.glb` or `.gltf`)
- 2-5 monster models (any names ending in `.glb` or `.gltf`)

#### What You're Looking For:
```
✅ modelA.glb (or similar name)
✅ monster01.glb
✅ monster02.glb
✅ monster03.glb

❌ model.zip (not supported, must be .glb/.gltf)
❌ model.fbx (not supported, must convert to .glb)
❌ model.obj (not supported, must convert to .glb)
```

To convert FBX/OBJ to GLB:
- Use: Blender (free), ShapeWays, babylon.js sandbox, or online converters
- Keep models under 10MB each for web performance

#### Place Files:
```
public/
└── models/
    ├── teddy/
    │   └── modelA.glb              ← Put your teddy bear file here
    │
    └── monsters/
        ├── monster01.glb           ← Put monster 1 here
        ├── monster02.glb           ← Put monster 2 here
        └── monster03.glb           ← Put monster 3 here
```

**File size guidelines:**
- Teddy: 0.5-5 MB (acceptable)
- Each monster: 0.5-10 MB (acceptable)
- Total: Keep under 50 MB for good loading

### Step 3: Update Configuration File

Edit `sceneConfig.ts` to match your file paths.

#### Find this section:
```typescript
models: {
  default: {
    path: "/models/teddy/modelA.glb",    // ← VERIFY THIS MATCHES
    scale: 1.5,
  },
  monsters: [
    { path: "/models/monsters/monster01.glb", scale: 1.5 },
    { path: "/models/monsters/monster02.glb", scale: 1.5 },
    { path: "/models/monsters/monster03.glb", scale: 1.5 },
    // ↑ VERIFY THESE MATCH YOUR FILES
  ],
}
```

#### If your files are named differently:

Example: Your files are named `bear.glb`, `witch.glb`, `zombie.glb`

Change to:
```typescript
models: {
  default: {
    path: "/models/teddy/bear.glb",       // ← Changed
    scale: 1.5,
  },
  monsters: [
    { path: "/models/monsters/witch.glb", scale: 1.5 },  // ← Changed
    { path: "/models/monsters/zombie.glb", scale: 1.5 }, // ← Changed
  ],
}
```

#### Path Rules:
```
✅ CORRECT: "/models/teddy/modelA.glb"
✅ CORRECT: "/models/monsters/monster01.glb"

❌ WRONG: "models/teddy/modelA.glb"           (missing /)
❌ WRONG: "/public/models/teddy/modelA.glb"   (don't include /public)
❌ WRONG: "./models/teddy/modelA.glb"         (don't use ./)
```

### Step 4: Test Everything

#### Quick Test:
1. Start your Next.js dev server:
   ```bash
   npm run dev
   ```

2. Open browser to `http://localhost:3000`

3. Should see:
   - [ ] Falling dust particles
   - [ ] Teddy bear in center
   - [ ] Green clock in top-right
   - [ ] No console errors

#### If anything missing, debug:

**Problem: White screen**
- Check browser console (F12 → Console tab)
- Look for error messages
- Verify paths in `sceneConfig.ts`

**Problem: Dust invisible**
- Increase dust count: `count: 3000`
- Increase dust size: `size: 0.15`

**Problem: Model not showing**
- Check console for 404 errors
- Verify file exists in `public/models/`
- Verify file path in `sceneConfig.ts` matches exactly
- Check file is valid GLB/GLTF format

---

## 📋 Folder Checklist

Use this to verify everything is in place:

```
public/
├── [ ] models/                    (folder exists)
│   ├── [ ] teddy/                 (folder exists)
│   │   └── [ ] modelA.glb         (file exists)
│   │
│   └── [ ] monsters/              (folder exists)
│       ├── [ ] monster01.glb      (file exists)
│       ├── [ ] monster02.glb      (file exists)
│       └── [ ] monster03.glb      (file exists)

sceneConfig.ts
├── [ ] models.default.path matches public/models/teddy/modelA.glb
├── [ ] models.monsters[0].path matches public/models/monsters/monster01.glb
├── [ ] models.monsters[1].path matches public/models/monsters/monster02.glb
└── [ ] models.monsters[2].path matches public/models/monsters/monster03.glb

app/
└── [ ] ParticleFieldVanilla.tsx (file exists and updated)
```

---

## 🎭 Adding More Monsters

Want to add a 4th, 5th, or more monsters?

### Step 1: Add File
Place your new monster file in `public/models/monsters/`:
```
public/models/monsters/
├── monster01.glb
├── monster02.glb
├── monster03.glb
├── monster04.glb        ← NEW
└── monster05.glb        ← NEW
```

### Step 2: Update Config
Edit `sceneConfig.ts`:
```typescript
monsters: [
  { path: "/models/monsters/monster01.glb", scale: 1.5 },
  { path: "/models/monsters/monster02.glb", scale: 1.5 },
  { path: "/models/monsters/monster03.glb", scale: 1.5 },
  { path: "/models/monsters/monster04.glb", scale: 1.5 },  ← ADD
  { path: "/models/monsters/monster05.glb", scale: 1.5 },  ← ADD
],
```

### Step 3: Save and Test
- Save the config file
- Refresh browser (Ctrl+F5 to hard refresh)
- When "13" is in time, should randomly pick from all 5 now

---

## 🔍 Verify File Permissions

Make sure files are readable:

#### Windows:
```
Right-click file → Properties → Security
Should have "Read" permission for current user
```

#### Mac/Linux:
```bash
# Check file permissions
ls -la public/models/teddy/modelA.glb

# Should show: -rw-r--r--
# If not, make readable:
chmod 644 public/models/teddy/modelA.glb
```

---

## 📊 File Size Best Practices

```
✅ SMALL (Fast loading)
modelA.glb:       500 KB
monster01.glb:    800 KB
Total:          ~3 MB

⚠️ MEDIUM (Acceptable)
modelA.glb:     2 MB
monster01.glb:  3 MB
Total:          ~8 MB

❌ LARGE (Too slow)
modelA.glb:     20 MB
monster01.glb:  25 MB
Total:          ~50+ MB
```

To reduce file size:
1. Use Blender to optimize mesh
2. Delete unused textures
3. Reduce texture resolution
4. Use mesh decimation/simplification

---

## 🌐 File Path Examples

### Example 1: Standard Names
```
Files:
public/models/teddy/teddy.glb
public/models/monsters/ghost.glb
public/models/monsters/zombie.glb
public/models/monsters/skeleton.glb

Config:
models: {
  default: { path: "/models/teddy/teddy.glb" },
  monsters: [
    { path: "/models/monsters/ghost.glb" },
    { path: "/models/monsters/zombie.glb" },
    { path: "/models/monsters/skeleton.glb" },
  ],
}
```

### Example 2: Numbered Names
```
Files:
public/models/teddy/model_a.glb
public/models/monsters/model_1.glb
public/models/monsters/model_2.glb

Config:
models: {
  default: { path: "/models/teddy/model_a.glb" },
  monsters: [
    { path: "/models/monsters/model_1.glb" },
    { path: "/models/monsters/model_2.glb" },
  ],
}
```

### Example 3: Complex Folder Names
```
Files:
public/models/teddy/season_winter/teddy.glb
public/models/monsters/horror/ghost.glb

Config:
models: {
  default: { path: "/models/teddy/season_winter/teddy.glb" },
  monsters: [
    { path: "/models/monsters/horror/ghost.glb" },
  ],
}
```

**Key Rule: Path must start with `/models/`**

---

## ✨ You're Ready!

Once you've:
1. ✅ Created folders
2. ✅ Placed model files
3. ✅ Updated config paths
4. ✅ Verified in browser

Your exhibition scene is ready to showcase! 🎨

---

## 🆘 Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| "model not found" error | Check file exists in public/models folder |
| Model loads but looks wrong | Model might need different scale in config |
| 404 error in console | Path in config doesn't match actual file path |
| Model is tiny/giant | Adjust `scale` value in config (1.0 = normal) |
| File won't load | Verify file format is .glb or .gltf, not .zip |

---

Done! Your asset structure is ready. 🚀
