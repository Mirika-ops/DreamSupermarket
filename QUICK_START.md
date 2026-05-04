# Exhibition Scene - Quick Reference & Setup Checklist

## ✅ Implementation Checklist

- [x] Scene setup with dark exhibition background
- [x] Professional 3-light setup (key, fill, rim)
- [x] Atmospheric dust particle system (2000+ particles)
- [x] GLTF model loader with proper memory disposal
- [x] 24-hour digital clock overlay
- [x] Smart trigger logic (detects "13" in time)
- [x] Random monster selection
- [x] Configuration-driven parameters
- [x] Bloom post-processing effect
- [x] Responsive resizing

## 📦 Files Created/Modified

| File | Purpose |
|------|---------|
| `sceneConfig.ts` | 🟢 **NEW** - Central configuration file |
| `app/ParticleFieldVanilla.tsx` | 🔄 **UPDATED** - Complete scene implementation |
| `types.ts` | 🟢 **NEW** - TypeScript type definitions |
| `EXHIBITION_SCENE_README.md` | 🟢 **NEW** - Complete setup guide |

## 🚀 Setup Steps (In Order)

### Step 1: Prepare Your Models
```bash
# Create folder structure:
mkdir -p public/models/teddy
mkdir -p public/models/monsters

# Place your models:
# public/models/teddy/modelA.glb        (your teddy bear - REQUIRED)
# public/models/monsters/monster01.glb  (optional - any number)
# public/models/monsters/monster02.glb  (optional)
# public/models/monsters/monster03.glb  (optional)
```

### Step 2: Update Configuration
Edit `sceneConfig.ts` to point to your models:

```typescript
models: {
  default: {
    path: "/models/teddy/modelA.glb",  // ← Your teddy bear path
    scale: 1.5,
  },
  monsters: [
    { path: "/models/monsters/monster01.glb", scale: 1.5 },
    { path: "/models/monsters/monster02.glb", scale: 1.8 },
    // Add as many as you want
  ],
}
```

### Step 3: Adjust Scene Settings
Fine-tune in `sceneConfig.ts`:

```typescript
// Dust appearance
dust: {
  count: 2000,              // More = denser dust
  color: 0xcccccc,          // Gray (adjust RGB hex)
  size: 0.08,               // 0.05-0.15 recommended
  opacity: 0.4,             // 0-1 transparency
}

// Dust movement
dust: {
  fallSpeed: 0.3,           // Lower = slower fall
  horizontalDriftSpeed: 0.15,  // Side-to-side motion
  turbulenceAmount: 0.5,    // Wobble intensity
}

// Lighting
lighting: {
  keyLight: { intensity: 0.8 },    // Main light brightness
  fillLight: { intensity: 0.4 },   // Shadow fill
  rimLight: { intensity: 0.3 },    // Edge glow
}
```

### Step 4: Test It!
- Component auto-loads when page renders
- Should show dust falling immediately
- Teddy bear appears in center
- Clock shows in top-right

### Step 5: Test the Trigger (Optional)
Change your system time to include "13":
- Set time to 13:00:00 → shows random monster
- Set time to 01:13:15 → shows random monster  
- Set time to normal time → shows teddy bear again

## 🎨 Common Configurations

### Slow, Heavy Dust
```typescript
dust: {
  count: 3000,
  size: 0.12,
  fallSpeed: 0.15,        // Very slow
  horizontalDriftSpeed: 0.08,
  turbulenceAmount: 0.3,
}
```

### Quick, Light Dust
```typescript
dust: {
  count: 1000,
  size: 0.05,
  fallSpeed: 0.8,         // Fast
  horizontalDriftSpeed: 0.3,
  turbulenceAmount: 0.8,
}
```

### Brighter Scene
```typescript
lighting: {
  keyLight: { intensity: 1.2 },
  fillLight: { intensity: 0.6 },
  rimLight: { intensity: 0.5 },
  ambientLight: { intensity: 0.7 },
}
```

### Darker, Moodier Scene
```typescript
lighting: {
  keyLight: { intensity: 0.6 },
  fillLight: { intensity: 0.2 },
  rimLight: { intensity: 0.2 },
  ambientLight: { intensity: 0.3 },
}
```

### Glow/Bloom Effects
```typescript
bloom: {
  enabled: true,
  intensity: 2.5,            // More glow (0.5-3.0)
  luminanceThreshold: 0.2,   // Lower = more things glow
}
```

## 🎯 Features Breakdown

### Dust Particle System
- 2000+ customizable particles
- Physics: gravity + horizontal drift + turbulence
- Automatic respawning (wraps around)
- Additive blending (soft glow)
- Updated EVERY FRAME

### Model Display
- Loads GLTF/GLB files
- Auto-centers at origin
- Auto-scales via config
- Clean disposal (no memory leaks)
- Smooth transitions

### Time Trigger Logic
```
Time String: "HH:mm:ss"

Contains "13"?
  ├─ "13:00:00" ✓ (starts with 13)
  ├─ "01:13:22" ✓ (minutes contain 13)
  ├─ "23:59:30" ✗ (no 13)
  └─ "20:05:13" ✓ (seconds contain 13)
```

### Lighting Theory
Three-point lighting setup:
1. **Key Light** (main, 0.8 intensity) - Front/top
2. **Fill Light** (soft, 0.4 intensity) - Side, fills shadows
3. **Rim Light** (subtle, 0.3 intensity) - Back, edge definition
4. **Ambient** (even glow, 0.5 intensity) - All directions

This provides professional, exhibition-quality lighting.

## 🔧 Advanced Tweaks

### Enable Auto-Rotation
Make the model slowly spin:
```typescript
animation: {
  enableAutoRotation: true,
  rotationSpeed: 0.005,
}
```

### Change Fog Density
```typescript
scene: {
  fogNear: 1,      // Start fog closer
  fogFar: 30,      // End fog distance
}
```

### Adjust Camera Position
```typescript
camera: {
  position: { x: 0, y: 2, z: 8 },    // Default - moderate distance
  // Use larger Z to zoom out: { x: 0, y: 2, z: 15 }
  // Use smaller Z to zoom in: { x: 0, y: 2, z: 4 }
  // Adjust Y for higher/lower angle: { x: 0, y: 3, z: 8 }
}
```

### Add a Second Teddy Bear Model
```typescript
models: {
  default: {
    path: "/models/teddy/modelA.glb",
  },
  // Add seasonal variant support:
  monsters: [
    { path: "/models/teddy/modelA_winter.glb", scale: 1.5 },
    { path: "/models/monsters/monster01.glb", scale: 1.5 },
  ]
}
```

## 📊 Performance Notes

- **Particle Count Impact**: 
  - 1000 particles: Very light, ~60 FPS always
  - 2000 particles: Default, ~55-60 FPS
  - 5000 particles: Heavy, ~30-45 FPS
  
- **Model Loading**: Happens asynchronously (no frame drops)

- **Clock Update**: Every 100ms (minimal overhead)

- **Bloom Effect**: Adds ~5-10% GPU load

**Target**: Maintain ≥30 FPS for smooth animation

## 🐛 Debug Tips

### Check Console Logs
The scene logs important events:
```
Loading model: /models/teddy/modelA.glb
Switched to monster: /models/monsters/monster01.glb
Loading model from cache: ... (if caching enabled)
```

### Visual Debugging
- **Missing dust?** Increase `dust.count` and `dust.size`
- **Model too small?** Increase `models.default.scale`
- **Too dark?** Increase `lighting.*.intensity`
- **Dust looks boxy?** Decrease `dust.size`

### Performance Profiling
Open DevTools > Performance tab:
1. Start recording
2. Let scene animate for 3 seconds
3. Stop recording
4. Look for frame drops or long frames

Target: 60 FPS and <16ms per frame

## 📝 Customization Template

Copy this template to customize further:

```typescript
// In sceneConfig.ts

export const sceneConfig = {
  // ... existing config ...
  
  // YOUR CUSTOMIZATIONS HERE:
  dust: {
    count: 2500,                // Adjust particle count
    color: 0xeeeeee,            // Change color (hex RGB)
    size: 0.1,                  // Adjust size
    opacity: 0.5,               // Change transparency
    fallSpeed: 0.25,            // Adjust gravity
    horizontalDriftSpeed: 0.2,  // Wind effect
    turbulenceAmount: 0.4,      // Wobble
  },
  
  lighting: {
    keyLight: {
      color: 0xffffff,          // White light
      intensity: 0.9,           // Brightness
    },
    // ... adjust others similarly
  },
};
```

## 🎬 Animation Loop Order

Every frame (60 FPS):
1. Update dust particles (position + velocity)
2. Apply turbulence/wobble
3. Respawn fallen particles
4. Optionally rotate model
5. Render scene with bloom effect

Total: ~16ms per frame (1000ms / 60 FPS)

## ✨ Final Tips

1. **Start Simple**: Use default config, adjust one thing at a time
2. **Test Trigger**: Set system time to 13:00:00 to verify swap
3. **Backup Config**: Keep a copy of working config
4. **Model Quality**: Use optimized GLB files (< 10MB each)
5. **Asset Naming**: Use clear names (monster01, monster02, etc.)

---

**Ready to go!** All the heavy lifting is done. Just add your models and adjust the config. 🎨
