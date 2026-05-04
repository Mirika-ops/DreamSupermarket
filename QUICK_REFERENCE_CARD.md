# Quick Reference Card

Print this or bookmark this page for quick access.

---

## 🚀 Launch In 3 Steps

```
1. FOLDERS
   mkdir -p public/models/teddy
   mkdir -p public/models/monsters

2. FILES  
   Copy: yourmodel.glb → public/models/teddy/modelA.glb
   Copy: monster01.glb → public/models/monsters/
   (Repeat for monster02, monster03, etc)

3. CONFIG
   Edit sceneConfig.ts:
   path: "/models/teddy/modelA.glb"
   path: "/models/monsters/monster01.glb"
```

---

## 📚 Which File To Read?

```
Want...                          Read...
─────────────────────────────────────────────────
Get started                      START_HERE.md
Setup folders                    ASSET_SETUP_GUIDE.md
Customize settings               CONFIG_CHEATSHEET.md
Fix a problem                    TROUBLESHOOTING.md
Understand system                ARCHITECTURE.md
Test everything                  VERIFICATION_CHECKLIST.md
Full details                     EXHIBITION_SCENE_README.md
Find anything                    DOCUMENTATION_INDEX.md
```

---

## ⚙️ Most Common Changes

```
Change       File                  What To Edit
─────────────────────────────────────────────────────
Dust speed   sceneConfig.ts        dust.fallSpeed
Dust count   sceneConfig.ts        dust.count
Brightness   sceneConfig.ts        lighting.*.intensity
Camera view  sceneConfig.ts        camera.position
Model size   sceneConfig.ts        models.default.scale
Glow effect  sceneConfig.ts        bloom.intensity
Monster list sceneConfig.ts        models.monsters[...]
```

---

## 🎨 Configuration Snippets

```typescript
// Make scene brighter
lighting: {
  keyLight: { intensity: 1.2 },
  ambientLight: { intensity: 0.7 }
}

// More visible dust
dust: {
  count: 3000,
  size: 0.12
}

// Faster dust
dust: {
  fallSpeed: 0.8
}

// Bigger model
models: {
  default: { scale: 2.0 }
}

// More particles
dust: { count: 4000 }

// Darker scene
scene: { backgroundColor: 0x050505 }
```

---

## 🛠️ Troubleshooting Quick Fixes

```
Problem              Quick Fix
──────────────────────────────────────────────
Models don't load    Check browser console (F12)
                     Verify file paths in config
                     
Dust invisible       Increase count: 3000
                     Increase size: 0.15
                     
Too dark             Increase lighting intensity
                     keyLight: 1.2, ambient: 0.7
                     
Too bright           Decrease lighting intensity
                     bloom.intensity: 0.8
                     
Clock missing        Check CSS z-index
                     Check console for errors
                     
Trigger not working  Set time to 13:00:00
                     Check monster paths
                     
Low FPS              Reduce dust count: 1000
                     Reduce bloom: 0.8
```

---

## 📊 Key Parameters

**Dust:**
- count: 2000 (how many)
- size: 0.08 (how big)
- opacity: 0.4 (transparency)
- fallSpeed: 0.3 (downward speed)
- horizontalDriftSpeed: 0.15 (side-to-side)
- turbulenceAmount: 0.5 (wobble)

**Lighting:**
- keyLight.intensity: 0.8 (main light)
- fillLight.intensity: 0.4 (shadow fill)
- rimLight.intensity: 0.3 (edge)
- ambientLight.intensity: 0.5 (overall)

**Bloom:**
- intensity: 1.5 (glow strength)
- luminanceThreshold: 0.3 (when things glow)

**Camera:**
- position.z: 8 (distance from model)
- position.y: 2 (height)

**Models:**
- default.path: "/models/teddy/modelA.glb"
- default.scale: 1.5 (size)
- monsters[]: array of monster paths/scales

---

## ⏰ Trigger Logic

```
Time Contains "13"?

13:00:00 ✓ (YES)
01:13:22 ✓ (YES)  
10:05:13 ✓ (YES)
23:59:59 ✗ (NO)

When YES:  Show random monster
When NO:   Show teddy bear
```

---

## 🎯 File Structure Required

```
public/
└── models/
    ├── teddy/
    │   └── modelA.glb
    └── monsters/
        ├── monster01.glb
        ├── monster02.glb
        └── monster03.glb
```

---

## 🔗 Config File Locations

```
sceneConfig.ts          (config file)
app/ParticleFieldVanilla.tsx  (main component)
types.ts                (type definitions)
public/models/          (model files)
```

---

## ✅ Verification Checklist

```
□ Models placed in public/models/
□ Paths updated in sceneConfig.ts
□ Dust falling visible
□ Model showing in center
□ Clock visible top-right
□ No errors in console (F12)
□ Smooth animation (60 FPS)
□ Trigger works (test at 13:00:00)
```

---

## 🚀 One-Command Launch

```bash
# Terminal
npm run dev

# Browser
http://localhost:3000
```

---

## 📞 Emergency Help

**Page blank?**
→ Open console (F12) → check errors → CONFIG_CHEATSHEET.md

**Models missing?**
→ Verify files in public/models/ → check paths → ASSET_SETUP_GUIDE.md

**Something broken?**
→ Check browser console → search TROUBLESHOOTING.md

**Need documentation?**
→ DOCUMENTATION_INDEX.md

**Want to learn?**
→ START_HERE.md (5 min) → ARCHITECTURE.md (15 min)

---

## 💭 Quick Hex Colors

```
0xffffff = White
0x000000 = Black
0xff0000 = Red
0x00ff00 = Green
0x0000ff = Blue
0xffff00 = Yellow
0xff8844 = Orange
0xcccccc = Light gray
0x0a0a0a = Dark (scene bg)
```

---

## 🎬 Parameter Ranges

```
dust.count: 500-5000
dust.size: 0.04-0.20
dust.opacity: 0.1-1.0
dust.fallSpeed: 0.05-1.0
lighting.*.intensity: 0-2.0
bloom.intensity: 0.5-3.0
camera.fov: 40-90
models.*.scale: 0.5-3.0
animation.rotationSpeed: 0.001-0.05
```

---

## 🏁 You're Ready!

**What you have:**
- ✅ Production-ready code
- ✅ Complete documentation
- ✅ Configuration system
- ✅ Professional scene

**What you need:**
- Your 3D models (.glb/.gltf files)
- 5 minutes to set up

**Next:**
→ Read START_HERE.md

---

**Bookmark this page!** 📌
