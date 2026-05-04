# Exhibition Scene Architecture

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ParticleFieldVanilla.tsx                     │
│                    (Main React Component)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   DustSystem │  │ ModelManager │  │ TimeDisplayManager   │  │
│  ├──────────────┤  ├──────────────┤  ├──────────────────────┤  │
│  │ - Particles  │  │ - GLTFLoader │  │ - Clock Display      │  │
│  │ - Animation  │  │ - Disposal   │  │ - "13" Trigger Logic │  │
│  │ - Spawn/     │  │ - Caching    │  │ - DOM Management     │  │
│  │   Respawn    │  │ - Scaling    │  │ - Events             │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│         │                │                       │              │
└─────────┼────────────────┼───────────────────────┼──────────────┘
          │                │                       │
          └────────┬───────┴───────────────────────┘
                   │
         ┌─────────▼────────────┐
         │   THREE.js Scene     │
         ├──────────────────────┤
         │ - Camera             │
         │ - Lights (x4)        │
         │ - Fog                │
         │ - Dust Points        │
         │ - Model Group        │
         └──────────────────────┘
                   │
         ┌─────────▼────────────┐
         │  Effect Composer     │
         ├──────────────────────┤
         │ - RenderPass         │
         │ - BloomEffect        │
         │ - Multiple Passes    │
         └──────────────────────┘
                   │
         ┌─────────▼────────────┐
         │   WebGL Renderer     │
         ├──────────────────────┤
         │ - Canvas Output      │
         │ - 60 FPS Animation   │
         └──────────────────────┘
```

## 📊 Data Flow Diagram

```
sceneConfig.ts (ALL PARAMETERS)
    │
    ├──────────────────────┬──────────────────────┬──────────────┐
    │                      │                      │              │
    ▼                      ▼                      ▼              ▼
  Scene Setup         Dust System            Model Paths      Lighting
  (colors, fog)       (count, speed)         (paths, scale)    (colors, intensity)
    │                      │                      │              │
    └──────────────────────┼──────────────────────┼──────────────┘
                           │
                 ┌─────────▼────────────┐
                 │ ParticleFieldVanilla │
                 └─────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
      ┌─────────┐    ┌──────────┐   ┌──────────────┐
      │  Setup  │    │ Animate  │   │ Handle Input │
      └─────────┘    └──────────┘   └──────────────┘
           │               │               │
           ├───────────────┼───────────────┤
           │               │               │
           ▼               ▼               ▼
      Scene Ready   60 FPS Loop    Clock Updates
                    - Update Dust   - Trigger Check
                    - Render        - Model Swap?
```

## 🔄 State Machine: Model Display

```
┌──────────────────┐
│  App Startup     │
└────────┬─────────┘
         │
         ▼
    Load Default
    (Teddy Bear)
         │
         ├─────────────────────────────┐
         │                             │
         ▼                             ▼
    Time Check                    Clock Updates
    Every 100ms                   (HTML overlay)
         │
         ├─ Time contains "13" ? ┐
         │                       │
    YES │                        │ NO
        │                        │
        ▼                        ▼
   Is showing                Is showing
   monster?                  teddy?
        │                        │
    NO │                        │ YES
        │                        │
        ▼                        ▼
   Random Monster          Stay with
   + Load                  Teddy
        │                        │
        └────────────┬───────────┘
                     │
                     ▼
            Animation Frame
            (60 FPS Render)

Legend:
- Every 100ms: Check time
- Every Frame: Render scene + particles
- On Switch: Dispose old, load new
```

## 🎨 Lighting Setup

```
                ┌────────────────────┐
                │   Key Light (0.8)  │
                │   Front/Top        │          ╱ Rim Light (0.3)
                │   Bright           │         ╱ Back/Edge
                └────────┬───────────┘        ╱ Subtle
                        ╱
                       ╱
                      ╱
         ┌────────────────────┐
     ┌───┤   3D MODEL         │
     │   │   (Center)         │
     │   └────────────────────┘
     │            │
     │            │ Ambient Light (0.5)
     │            │ All directions
     │            │
     ▼            │
  ┌──────────────────────┐
  │ Fill Light (0.4)     │
  │ Side/Shadow Fill     │
  │ Soft blue tint       │
  └──────────────────────┘

Result: Professional 3-point lighting
suitable for product photography
```

## 💾 Memory Management

### Model Loading & Disposal

```
Model A (Teddy)
    │
    ├─ Loaded into scene
    │  
    └─ Time contains "13"?
         │
         YES
         ▼
    ┌──────────────────────┐
    │ Select Random Monster│
    └──────┬───────────────┘
           │
           ▼
    ┌──────────────────────┐
    │ Dispose Model A:     │
    │ - Traverse object    │
    │ - Dispose geometry   │
    │ - Dispose materials  │
    │ - Remove from scene  │
    └──────────────────────┘
           │
           ▼
    ┌──────────────────────┐
    │ Load Model B (Monster)
    └──────────────────────┘
           │
           ▼
    Model B in scene
    
    Time no longer contains "13"?
         │
         YES
         ▼
    Repeat: Dispose B, Load A
```

### Particle System Memory

```
Initialization:
  - Create Float32Array (count * 3)  ← Positions
  - Create Float32Array (count * 3)  ← Velocities
  - Create BufferGeometry
  - Create PointsMaterial

Every Frame:
  - Update particle positions (CPU)
  - Set geometry.attributes.position.needsUpdate = true
  - GPU updates buffer

Cleanup:
  - geometry.dispose()
  - material.dispose()
  - Remove from scene
```

## 📈 Performance Profile

```
Frame Budget: ~16ms (for 60 FPS)

Per Frame Breakdown:
├─ Update Dust (CPU):        ~3ms   (2000 particles)
├─ Update Geometry Buffer:   ~1ms   (if changed)
├─ Rotate Model (optional):  <0.5ms
├─ Render Scene (GPU):       ~8ms   
├─ Bloom Post-Process:       ~3ms   (largest GPU cost)
└─ Misc (browser overhead):  ~0.5ms
                      ──────────
                      Total: ~15.5ms ✓ (within budget)

Safe limits:
- Dust count: 1000-5000
- Bloom intensity: 0.5-3.0
- Camera resolution: Full HD+
```

## 🔌 Integration Points

### Clock Update Loop
```typescript
setInterval(() => {
  timeManager.update();        // Get new time
  
  if (trigger.contains13()) {
    if (!showingMonster) {
      modelManager.swap(randomMonster);
    }
  } else {
    if (showingMonster) {
      modelManager.swap(teddyBear);
    }
  }
}, 100);  // Check 10x per second
```

### Animation Loop
```typescript
function animate() {
  requestAnimationFrame(animate);
  
  // Per-frame updates
  dustSystem.update(deltaTime, config);
  
  if (config.animation.enableAutoRotation) {
    model.rotation.y += config.animation.rotationSpeed;
  }
  
  // Render
  composer.render();  // Includes bloom
  
  // ~16ms total
}
```

### Scene Graph Structure

```
Scene
├── Cameras
│   └── PerspectiveCamera
├── Lights
│   ├── DirectionalLight (Key)
│   ├── DirectionalLight (Fill)
│   ├── DirectionalLight (Rim)
│   └── AmbientLight
├── Objects
│   ├── Points (Dust particles)
│   └── Group (GLTF Model)
│       ├── Mesh 1
│       ├── Mesh 2
│       └── ...
└── Fog

Renderer
└── Canvas
    └── rendered output

Composer (Post-processing)
├── RenderPass
└── EffectPass (Bloom)
```

## 🎯 Config Cascade

```
sceneConfig.ts
    │
    ├─ Scene Setup
    │  └─ Passed to THREE.Scene()
    │
    ├─ Camera Config
    │  └─ Passed to PerspectiveCamera()
    │
    ├─ Lighting Config
    │  └─ Passed to DirectionalLight() x3, AmbientLight()
    │
    ├─ Dust Config
    │  └─ Passed to DustParticleSystem
    │     └─ Controls spawn, speed, size
    │
    ├─ Model Config
    │  └─ Passed to ModelManager
    │     └─ Loaded via GLTFLoader
    │     └─ Scaled & positioned
    │
    ├─ Bloom Config
    │  └─ Passed to BloomEffect
    │     └─ Controls glow intensity
    │
    └─ Animation Config
       └─ Passed to animate loop
           └─ Controls model rotation

Single source of truth: sceneConfig.ts
All parameters adjustable without code changes
```

## 🔗 Dependency Graph

```
Three.js (core)
├─ GLTFLoader (model loading)
└─ Helpers (Math)

postprocessing (effects)
├─ EffectComposer
├─ RenderPass
├─ EffectPass
└─ BloomEffect

React (component wrapper)
└─ useEffect (lifecycle)
└─ useRef (DOM/object references)

sceneConfig.ts (configuration)
└─ All parameters

ParticleFieldVanilla.tsx (main)
├─ Orchestrates everything
├─ Manages lifecycle
└─ Exports component
```

---

This architecture is designed for:
- ✅ Maintainability (clear separation of concerns)
- ✅ Extensibility (easy to add features)
- ✅ Performance (optimized rendering loop)
- ✅ Debuggability (clear data flow)
- ✅ Configurability (all params in one file)
