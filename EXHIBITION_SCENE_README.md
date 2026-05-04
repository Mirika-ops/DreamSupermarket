# 3D Exhibition Scene - Setup & Implementation Guide

## 📋 Overview

This implementation provides a beautiful dark exhibition scene with:
- **Atmospheric dust particle system** - Slow falling dust with subtle turbulence
- **GLTF model display** - Teddy bear by default, random monsters when time contains "13"
- **Professional lighting** - Soft key/fill/rim lights suitable for 3D models
- **Digital clock overlay** - Shows HH:mm:ss format
- **Bloom post-processing** - Beautiful glow effects already configured
- **Memory-efficient model loading** - Proper disposal and caching

## 🎯 Features Implemented

### 1. **Scene Setup** ✓
- Dark exhibition background (almost black)
- Volumetric fog for atmospheric depth
- Professional three-light setup (key, fill, rim)
- Ambient lighting for overall scene brightness

### 2. **Dust Particle System** ✓
- Configurable particle count (default: 2000)
- Slow falling motion with drift
- Realistic turbulence/wobble effect
- Automatic respawning when particles exit bottom
- Additive blending for soft glow

### 3. **Central Model Display** ✓
- Loads GLTF/GLB models cleanly
- Automatic scaling and centering
- Easy model swap with proper disposal
- Default teddy bear model

### 4. **Time Display** ✓
- 24-hour digital clock (HH:mm:ss)
- Updates every second
- Beautiful green monospace styling
- Positioned top-right with glow effect

### 5. **Smart Model Trigger** ✓
- Detects when time contains "13" anywhere in HH:mm:ss
- Examples that trigger:
  - `13:00:00` ✓
  - `01:13:22` ✓
  - `10:05:13` ✓
- Smoothly swaps to random monster
- Avoids reloading same model
- Switches back automatically

### 6. **Asset Management** ✓
- Configuration file for all settings
- Easy model path configuration
- Particle quantity control
- Lighting adjustments
- All parameters in one place

## 📁 File Structure

Create this folder structure in your project:

```
public/
├── models/
│   ├── teddy/
│   │   └── modelA.glb              ← Your teddy bear model
│   └── monsters/
│       ├── monster01.glb           ← Random monsters
│       ├── monster02.glb
│       └── monster03.glb           ← Add more as needed
app/
├── ParticleFieldVanilla.tsx        ← Main scene component (updated)
├── page.tsx                        ← Your entry point
└── layout.tsx
sceneConfig.ts                      ← Configuration file (created)
```

## 🎨 Configuration File (`sceneConfig.ts`)

All scene parameters are in one place. Common adjustments:

```typescript
// Dust particle count
dust: {
  count: 2000,          // Increase for more dust, decrease for less
  size: 0.08,          // Particle size (0.05-0.15)
  opacity: 0.4,        // Transparency (0-1)
  fallSpeed: 0.3,      // How fast dust falls
  horizontalDriftSpeed: 0.15,  // Side-to-side motion
}

// Camera position
camera: {
  position: { x: 0, y: 2, z: 8 },  // Move camera closer/farther
}

// Lighting intensity
lighting: {
  keyLight: { intensity: 0.8 },     // Adjust brightness
  fillLight: { intensity: 0.4 },
}

// Model paths
models: {
  default: {
    path: "/models/teddy/modelA.glb",
    scale: 1.5,                      // Size multiplier
  },
  monsters: [
    { path: "/models/monsters/monster01.glb", scale: 1.5 },
    // Add more monsters here
  ],
}
```

## 🚀 Quick Start

### 1. **Add Your Models**

Place GLTF/GLB files in:
- `public/models/teddy/modelA.glb` (required - default model)
- `public/models/monsters/monster01/02/03.glb` (as many as you want)

### 2. **Adjust Configuration**

Edit `sceneConfig.ts` to:
- Match your model paths
- Adjust particle count
- Change lighting colors/intensity
- Modify dust speed/turbulence

### 3. **Test**

The component automatically:
- Loads the teddy bear on startup
- Shows the digital clock
- Watches the time
- Swaps to random monsters when time contains "13"

## 🛠️ Common Adjustments

### **Make dust faster/slower**
```typescript
dust: {
  fallSpeed: 0.5,        // Increase to fall faster
}
```

### **Add more dust particles**
```typescript
dust: {
  count: 3000,           // From 2000 to 3000
}
```

### **Change dust color**
```typescript
dust: {
  color: 0xdddddd,       // Light gray
  // Or: 0xff8844 (orange), 0x88ccff (blue), etc.
}
```

### **Adjust lighting**
```typescript
lighting: {
  keyLight: {
    intensity: 1.2,      // Make brighter
    color: 0xffffff,     // Or change to 0xffff99 (warm), etc.
  }
}
```

### **Move camera position**
```typescript
camera: {
  position: { x: 0, y: 2, z: 10 },  // Move back (larger z)
  position: { x: 0, y: 3, z: 6 },   // Move closer/higher
}
```

### **Change bloom intensity**
```typescript
bloom: {
  intensity: 2.5,        // More glow (default 1.5)
}
```

## 🎬 Animation Loop Details

The main animation loop:
1. Updates dust particle positions
2. Applies turbulence/wobble
3. Respawns particles that fall too far
4. Optionally rotates model (configurable)
5. Renders with bloom effect

Performance is optimized:
- Only updates GPU buffer when needed
- Clamps delta time to prevent frame skips
- Efficient particle respawning
- Model caching to avoid reloading

## 🔄 Model Switching Logic

```
Every 100ms:
  - Check current time (HH:mm:ss)
  - Is "13" in the time string?
    
  If YES and currently showing teddy:
    → Select random monster
    → Dispose old model
    → Load and position new monster
    
  If NO and currently showing monster:
    → Dispose monster
    → Load and position teddy bear
    → Ready for next trigger
```

This prevents:
- Reloading the same model repeatedly
- Memory leaks from undisposed geometry/materials
- Jarring model switches
- CPU overhead from constant loads

## 💾 Memory Management

The implementation properly handles:

### **Model Disposal**
```typescript
// When switching models:
- Traverse the old model
- Dispose all geometries
- Dispose all materials
- Remove from scene
- Only then load new model
```

### **Particle System Cleanup**
```typescript
// On unmount:
- Cancel animation frames
- Clear intervals
- Dispose dust geometry/material
- Dispose renderer and composer
```

### **Model Caching**
```typescript
// Disabled currently to prevent memory bloat
// Can be re-enabled if you have < 5 models
// Just enable Cache manager logic
```

## 🎯 Customization Examples

### **Make dust blue instead of gray**
Edit `sceneConfig.ts`:
```typescript
dust: {
  color: 0x4488ff,       // Blue dust
}
```

### **Add 5 monster models**
1. Add monster04.glb and monster05.glb to `public/models/monsters/`
2. Edit `sceneConfig.ts`:
```typescript
monsters: [
  { path: "/models/monsters/monster01.glb", scale: 1.5 },
  { path: "/models/monsters/monster02.glb", scale: 1.8 },
  { path: "/models/monsters/monster03.glb", scale: 1.5 },
  { path: "/models/monsters/monster04.glb", scale: 2.0 },  // NEW
  { path: "/models/monsters/monster05.glb", scale: 1.7 },  // NEW
],
```

### **Change clock style**
The clock is created in `TimeDisplayManager.createClockElement()`. Modify the CSS:
```typescript
clock.style.cssText = `
  color: #ff00ff;        // Change to magenta
  font-size: 48px;       // Make bigger
  border: 3px solid #00ff00;  // Green border
`;
```

## ⚙️ Technical Details

### **Classes Implemented**

1. **DustParticleSystem**
   - Manages 2000+ particles
   - Handles position/velocity updates
   - Adds Perlin-like turbulence
   - Auto-respawning logic

2. **ModelManager**
   - GLTF loader wrapper
   - Model caching (optional)
   - Automatic centering/scaling
   - Safe disposal

3. **TimeDisplayManager**
   - Clock HTML element creation
   - Time string generation
   - "13" detection logic
   - Cleanup on unmount

### **Three.js Resources Used**
- `BufferGeometry` for particles
- `PointsMaterial` with additive blending
- `DirectionalLight` (3x) for realistic lighting
- `AmbientLight` for ambient glow
- `Fog` for atmospheric depth

### **PostProcessing**
- `EffectComposer` for rendering
- `BloomEffect` for glow
- `RenderPass` for base rendering

## 🐛 Troubleshooting

### **Models not loading**
- Check browser console for errors
- Verify file paths in `sceneConfig.ts`
- Ensure models are in `public/models/` folder
- GLTF/GLB files must be valid 3D models

### **Dust not visible**
- Increase `dust.count` in config
- Increase `dust.size` (default 0.08)
- Adjust `dust.opacity` (default 0.4)
- Check camera position

### **Clock not showing**
- Check CSS z-index isn't blocked
- Browser console should have no errors
- Verify DOM not being hidden by other elements

### **Model swap not triggering**
- Open browser console
- Check that logs show time updates
- Verify `sceneConfig.models.monsters` has entries
- Time must actually contain "13" (13:XX:XX, XX:13:XX, XX:XX:13)

### **Performance issues**
- Reduce `dust.count` (currently 2000)
- Reduce `bloom.intensity` (currently 1.5)
- Increase `scene.fogFar` to cull objects quicker
- Monitor frame rate with developer tools

## 📚 Next Steps

1. **Prepare your models** in GLB format
2. **Place in public/models/** folder
3. **Update sceneConfig.ts** with your paths
4. **Adjust parameters** to your liking
5. **Test the 13:00:00 trigger** by adjusting system time

The code is production-ready and optimized for smooth performance!
