# Configuration Cheat Sheet

Quick reference for all configurable parameters in `sceneConfig.ts`

## 🎨 Scene Colors & Appearance

```typescript
scene: {
  backgroundColor: 0x0a0a0a,    // Background color (hex)
  fogColor: 0x000000,            // Fog color (hex)
  fogNear: 1,                    // Fog start distance
  fogFar: 50,                    // Fog end distance
}

// Change to lighter scene:
backgroundColor: 0x1a1a1a,  // Lighter gray
fogColor: 0x222222,         // Lighter fog

// Change to warmer scene:
backgroundColor: 0x1a0f05,  // Dark brown
fogColor: 0x2a1505,         // Brown fog
```

## 🎥 Camera Control

```typescript
camera: {
  fov: 75,                                    // Field of view (degrees)
  position: { x: 0, y: 2, z: 8 },           // Camera position
  lookAt: { x: 0, y: 1, z: 0 },             // Where camera looks
}

// Zoom in (closer to model)
position: { x: 0, y: 2, z: 4 }

// Zoom out (farther from model)
position: { x: 0, y: 2, z: 15 }

// Look higher/lower
lookAt: { x: 0, y: 2, z: 0 }  // Look higher
lookAt: { x: 0, y: 0, z: 0 }  // Look at center
lookAt: { x: 0, y: -1, z: 0 } // Look lower
```

## 💡 Lighting (All Intensities 0-2)

```typescript
lighting: {
  keyLight: {
    color: 0xffffff,           // Light color (hex)
    intensity: 0.8,            // Brightness 0-2
    position: { x: 5, y: 5, z: 5 },
  },
  fillLight: {
    color: 0xaaaaff,           // Soft blue fill
    intensity: 0.4,
    position: { x: -3, y: 3, z: -5 },
  },
  rimLight: {
    color: 0xffaaaa,           // Warm rim
    intensity: 0.3,
    position: { x: 0, y: 8, z: -10 },
  },
  ambientLight: {
    color: 0x333333,
    intensity: 0.5,
  },
}

// Examples:

// Brighter overall
keyLight: { intensity: 1.2 }
fillLight: { intensity: 0.6 }
ambientLight: { intensity: 0.8 }

// Darker/moodier
keyLight: { intensity: 0.5 }
fillLight: { intensity: 0.2 }
ambientLight: { intensity: 0.3 }

// Warmer (orange) lights
keyLight: { color: 0xffcc88, intensity: 0.8 }
fillLight: { color: 0xff9944, intensity: 0.4 }

// Cooler (blue) lights
keyLight: { color: 0x88ccff, intensity: 0.8 }
fillLight: { color: 0x88ccff, intensity: 0.4 }
```

## ✨ Bloom (Glow Effect)

```typescript
bloom: {
  enabled: true,                 // Turn on/off
  intensity: 1.5,                // Glow strength (0.5-3.0)
  luminanceThreshold: 0.3,       // Threshold (0.1-0.5)
}

// Subtle bloom
intensity: 0.8,
luminanceThreshold: 0.4,

// Heavy glow
intensity: 2.5,
luminanceThreshold: 0.1,

// No bloom
enabled: false,
```

## 💨 Dust Particle System

### Count & Size
```typescript
dust: {
  count: 2000,              // Particle count
  size: 0.08,               // Size in units
  opacity: 0.4,             // Transparency 0-1
}

// Dense dust cloud
count: 3500,
size: 0.12,
opacity: 0.5,

// Sparse, light dust
count: 800,
size: 0.05,
opacity: 0.3,
```

### Movement & Physics
```typescript
dust: {
  fallSpeed: 0.3,           // Downward speed
  horizontalDriftSpeed: 0.15,  // Side-to-side
  turbulenceAmount: 0.5,    // Wobble/shake
}

// Fast, swirling dust
fallSpeed: 0.8,
horizontalDriftSpeed: 0.4,
turbulenceAmount: 0.8,

// Slow, gentle dust
fallSpeed: 0.1,
horizontalDriftSpeed: 0.05,
turbulenceAmount: 0.2,
```

### Spawn Area
```typescript
dust: {
  spawnAreaX: 15,           // Width of spawn zone
  spawnAreaZ: 15,           // Depth of spawn zone
  spawnHeight: 20,          // Height where spawned
  respawnThreshold: -5,     // Y position to respawn
}

// Wider spawn area
spawnAreaX: 25,
spawnAreaZ: 25,

// Narrower spawn area
spawnAreaX: 8,
spawnAreaZ: 8,
```

## 🎭 Model Display

### Default Model (Teddy Bear)
```typescript
models: {
  default: {
    path: "/models/teddy/modelA.glb",
    scale: 1.5,
    position: { x: 0, y: 0, z: 0 },
    rotation: { x: 0, y: 0, z: 0 },
  },
}

// Make model bigger
scale: 2.0,

// Make model smaller
scale: 0.75,

// Position higher
position: { x: 0, y: 2, z: 0 },

// Position to the side
position: { x: 3, y: 0, z: 0 },

// Rotate model (in radians)
rotation: { x: 0, y: 3.14159, z: 0 },  // Flip 180°
```

### Monster Models
```typescript
models: {
  monsters: [
    { path: "/models/monsters/monster01.glb", scale: 1.5 },
    { path: "/models/monsters/monster02.glb", scale: 1.8 },
    { path: "/models/monsters/monster03.glb", scale: 1.5 },
  ],
}

// Add a 4th monster
{ path: "/models/monsters/monster04.glb", scale: 2.0 },

// Different scales for each
monster01: scale: 1.2,
monster02: scale: 1.8,  // Bigger
monster03: scale: 0.9,  // Smaller
```

## 🎬 Animation

```typescript
animation: {
  enableAutoRotation: false,    // Rotate model?
  rotationSpeed: 0.005,         // Rotation speed (rad/frame)
}

// Enable rotation
enableAutoRotation: true,

// Speed up rotation
rotationSpeed: 0.02,

// Slow down rotation
rotationSpeed: 0.001,
```

## ⏰ Trigger Logic (Automatic)

```typescript
trigger: {
  digit: "13",  // Swap models when time contains "13"
}

// You only change this if you want different trigger:
digit: "42",    // Trigger on 42:XX:XX, XX:42:XX, XX:XX:42
digit: "7",     // Trigger on 07:XX:XX, XX:07:XX, XX:XX:07
```

---

## 🎨 Complete Config Examples

### Preset: Soft & Peaceful
```typescript
dust: {
  count: 1500,
  color: 0xdddddd,
  size: 0.1,
  opacity: 0.5,
  fallSpeed: 0.15,
  horizontalDriftSpeed: 0.1,
  turbulenceAmount: 0.3,
}
bloom: { intensity: 1.0 }
lighting: {
  keyLight: { intensity: 0.7 },
  fillLight: { intensity: 0.35 },
  ambientLight: { intensity: 0.6 },
}
```

### Preset: Dramatic & Dark
```typescript
dust: {
  count: 2500,
  color: 0x888888,
  size: 0.08,
  opacity: 0.3,
  fallSpeed: 0.4,
  horizontalDriftSpeed: 0.2,
  turbulenceAmount: 0.7,
}
bloom: { intensity: 2.0 }
lighting: {
  keyLight: { intensity: 0.9 },
  fillLight: { intensity: 0.3 },
  ambientLight: { intensity: 0.4 },
}
scene: { backgroundColor: 0x050505 }
```

### Preset: Bright & Clean
```typescript
dust: {
  count: 1000,
  color: 0xeeeeee,
  size: 0.06,
  opacity: 0.2,
  fallSpeed: 0.2,
}
bloom: { intensity: 0.5 }
lighting: {
  keyLight: { intensity: 1.2 },
  fillLight: { intensity: 0.6 },
  ambientLight: { intensity: 0.8 },
}
scene: { backgroundColor: 0x1a1a1a }
```

### Preset: Warm & Inviting
```typescript
dust: {
  color: 0xffddaa,           // Warm dust
}
lighting: {
  keyLight: { color: 0xffddaa, intensity: 0.9 },
  fillLight: { color: 0xff9944, intensity: 0.5 },
  rimLight: { color: 0xffcc88, intensity: 0.4 },
}
scene: { backgroundColor: 0x0f0a05 }  // Warm black
```

---

## 🔍 Hex Color Reference

```
0xffffff = White
0x000000 = Black
0xff0000 = Red
0x00ff00 = Green
0x0000ff = Blue
0xffff00 = Yellow (red + green)
0xff00ff = Magenta (red + blue)
0x00ffff = Cyan (green + blue)

0xff8844 = Orange
0xcccccc = Light gray
0x666666 = Dark gray
0xffeedd = Soft peach
0xaaaaff = Soft blue
0xffaaaa = Soft red
```

Format: `0xRRGGBB` where RR/GG/BB are hex values (00-FF)

---

## 📐 Position/Scale Reference

```
Position: { x, y, z }
- x: Left (-) / Right (+)
- y: Down (-) / Up (+)
- z: Back (-) / Forward (+)

Scale: multiplier
- 0.5 = half size
- 1.0 = normal size
- 2.0 = double size

Rotation: radians
- 0 = no rotation
- 3.14159 ≈ π = 180° flip
- 6.28318 ≈ 2π = 360° full rotation
```

---

## ⚡ Quick Tweaks

**Scene too dark?**
```typescript
lighting: {
  keyLight: { intensity: 1.0 },
  ambientLight: { intensity: 0.7 },
}
```

**Dust invisible?**
```typescript
dust: {
  count: 3000,
  size: 0.12,
  opacity: 0.6,
}
```

**Model too small/big?**
```typescript
models: {
  default: { scale: 2.0 },  // 2x bigger
  monsters: [
    { path: "...", scale: 2.0 },  // All bigger
  ],
}
```

**Bloom too intense?**
```typescript
bloom: { intensity: 0.8 }
```

**Camera too far/close?**
```typescript
camera: { position: { x: 0, y: 2, z: 6 } }  // Closer (z smaller)
```

---

See **EXHIBITION_SCENE_README.md** for more details on each parameter.
