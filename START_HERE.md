# ⚡ 5-Minute Quick Start

Get the exhibition scene running in 5 minutes.

## Step 1: Create Folders (30 seconds)

Windows (PowerShell):
```powershell
mkdir public\models\teddy
mkdir public\models\monsters
```

Mac/Linux:
```bash
mkdir -p public/models/teddy
mkdir -p public/models/monsters
```

## Step 2: Add Models (1 minute)

Copy your 3D model files to:
- `public/models/teddy/modelA.glb` (teddy bear)
- `public/models/monsters/monster01.glb` (any monsters)
- `public/models/monsters/monster02.glb`
- `public/models/monsters/monster03.glb` (optional)

Files must be:
- ✅ `.glb` or `.gltf` format
- ✅ Less than 10MB each

*Don't have models? Use Sketchfab or remixable 3D models*

## Step 3: Update Config (1 minute)

Edit `sceneConfig.ts` and find:
```typescript
models: {
  default: {
    path: "/models/teddy/modelA.glb",     // ← Check this matches your file
    scale: 1.5,
  },
  monsters: [
    { path: "/models/monsters/monster01.glb", scale: 1.5 },
    { path: "/models/monsters/monster02.glb", scale: 1.5 },
    { path: "/models/monsters/monster03.glb", scale: 1.5 },
  ],  // ← Check these match your files
}
```

**If your filenames are different**, update the paths.

## Step 4: Test (1 minute)

```bash
npm run dev
```

Open browser to `http://localhost:3000`

You should see:
- ✅ Falling dust particles
- ✅ Teddy bear in center
- ✅ Green clock top-right
- ✅ Soft professional lighting

## Step 5: Test Trigger (Optional, 30 seconds)

1. Set system time to 13:00:00
2. Wait 2 seconds
3. Model should change to random monster
4. Set time back to normal
5. Should change back to teddy

---

## 🎉 Done!

Your exhibition scene is live!

---

## 🎨 Quick Customizations

### Make Dust Faster
```typescript
dust: { fallSpeed: 0.8 }
```

### Make Scene Brighter
```typescript
lighting: {
  keyLight: { intensity: 1.2 },
  ambientLight: { intensity: 0.7 }
}
```

### Add More Monsters
1. Add file to `public/models/monsters/monster04.glb`
2. Add to config:
   ```typescript
   { path: "/models/monsters/monster04.glb", scale: 1.5 }
   ```

### Change Model Size
```typescript
models: {
  default: { scale: 2.0 }  // Bigger
}
```

### See All Options
Read `CONFIG_CHEATSHEET.md`

---

## 🚨 Common Issues

**Models not showing?**
- Check browser console (F12)
- Verify file paths in `sceneConfig.ts` match actual files
- Check files exist in `public/models/`

**Dust invisible?**
- Increase: `count: 3000`, `size: 0.15`

**Too dark?**
- Increase lighting intensity values

**Need help?**
See `TROUBLESHOOTING.md`

---

**That's it! You're ready to go. 🚀**

For more details, see the other documentation files.
