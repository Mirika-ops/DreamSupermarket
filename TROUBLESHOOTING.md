# Troubleshooting Guide

Complete troubleshooting reference for the 3D exhibition scene.

## 🔴 Critical Issues

### Issue: Page Shows White/Black Screen

**Symptoms:**
- Page loads but displays blank canvas
- No dust, no model, no clock
- May see "Loading exhibition..." text briefly

**Diagnosis Steps:**
1. Open Developer Tools (F12 or Right-click → Inspect)
2. Go to Console tab
3. Look for error messages in red
4. Look for "Failed to load" messages

**Common Errors & Fixes:**

#### Error: "THREE is not defined"
```
Problem: Three.js not installed properly
Solution: Run: npm install three
```

#### Error: "Cannot find module 'postprocessing'"
```
Problem: Missing postprocessing library
Solution: Run: npm install postprocessing
```

#### Error: "Failed to load model: /models/teddy/modelA.glb"
```
Problem: File doesn't exist at that path
Solution:
  1. Check file exists in public/models/teddy/
  2. Verify file path in sceneConfig.ts
  3. Check path starts with / (not ./)
  4. Check filename spelling (case-sensitive on Linux)
```

#### Error: "Cannot read property 'x' of undefined"
```
Problem: Config file not imported correctly
Solution:
  1. Verify import line: import { sceneConfig } from '../sceneConfig';
  2. Check sceneConfig.ts exists in root
  3. Check export: export const sceneConfig = {...}
```

**If still blank after fixes:**
1. Stop dev server (Ctrl+C)
2. Clear cache: `npm run build` then restart
3. Hard refresh browser (Ctrl+Shift+R)
4. Check if Next.js complains about CSS or imports

---

### Issue: Component Doesn't Load At All

**Symptoms:**
- Page shows nothing
- No errors in console
- "Loading exhibition..." doesn't appear

**Fix:**
1. Check `page.tsx` imports ParticleFieldVanilla:
   ```typescript
   import ParticleFieldVanilla from '@/app/ParticleFieldVanilla';
   ```

2. Check ParticleFieldVanilla.tsx has `'use client'` at top

3. Verify ParticleFieldVanilla is default export:
   ```typescript
   export default function ParticleFieldVanilla() { ... }
   ```

---

## 🟠 Model Loading Issues

### Issue: Model Doesn't Appear / "404" Error

**Symptoms:**
- Clock and dust visible, but no model in center
- Console shows: `Failed to load model: /models/...`
- Console shows: 404 error for model file

**Fix Checklist:**
- [ ] File exists in `public/models/teddy/modelA.glb`?
- [ ] File name matches exactly in `sceneConfig.ts`?
- [ ] Path starts with `/` (forward slash)?
- [ ] Path doesn't start with `./` or `../`?
- [ ] File is `.glb` or `.gltf`, not `.zip` or `.fbx`?
- [ ] File path uses forward slashes `/`, not backslashes `\`?

**Example Fixes:**
```typescript
// ❌ WRONG
path: "models/teddy/modelA.glb"           // Missing initial /
path: "/public/models/teddy/modelA.glb"   // Don't include /public
path: "C:\\Users\\...\\modelA.glb"        // Absolute path won't work
path: "./models/teddy/modelA.glb"         // Don't use ./

// ✅ CORRECT
path: "/models/teddy/modelA.glb"
path: "/models/monsters/monster01.glb"
```

---

### Issue: Model Loads But Looks Wrong

**Symptoms:**
- Model appears but is tiny/giant
- Model is rotated strange way
- Model has pink/black texture (missing materials)
- Model appears distorted

**Fix by Issue Type:**

#### Model is Tiny:
```typescript
// Increase scale
models: {
  default: {
    scale: 3.0,  // Increase from 1.5
  }
}
```

#### Model is Giant:
```typescript
// Decrease scale
models: {
  default: {
    scale: 0.5,  // Decrease from 1.5
  }
}
```

#### Model is Rotated Wrong:
```typescript
// Adjust initial rotation (in radians)
models: {
  default: {
    rotation: { x: 0, y: 3.14159, z: 0 }  // Flip 180°
  }
}
```

#### Missing Textures (Pink/Black):
- GLTF file may be missing textures
- Re-export from 3D program with "export textures" option
- Check file format: `.gltf` files need separate texture files

---

### Issue: Model Doesn't Swap When Time Has "13"

**Symptoms:**
- Time is 13:00:00 or contains "13" somewhere
- Model doesn't change to monster
- No console logs about switching

**Diagnosis:**
1. Open Console (F12)
2. Set system time to exactly 13:00:00
3. Wait 2 seconds
4. Look for console message: "Switched to monster"

**If no message appears:**
- [ ] Monster paths in config are correct?
- [ ] Monster files exist in `public/models/monsters/`?
- [ ] JavaScript executing (no errors above)?
- [ ] Wait 2 seconds after time change?

**Force Test:**
Temporarily change trigger digit in `sceneConfig.ts`:
```typescript
trigger: {
  digit: "7",  // Change to "7"
}
```

Then set system time to 07:00:00 or similar. If it swaps with "7", the system works and "13" monsters just aren't set up.

---

## 🟡 Visual/Display Issues

### Issue: Dust Particles Invisible

**Symptoms:**
- Clock and model visible, but no dust falling
- Dark background but no particle motion

**Fix Progression:**

Step 1 - Increase particle count:
```typescript
dust: {
  count: 3000,  // Increase from 2000
}
```

Step 2 - Increase particle size:
```typescript
dust: {
  size: 0.15,  // Increase from 0.08
}
```

Step 3 - Increase particle opacity:
```typescript
dust: {
  opacity: 0.7,  // Increase from 0.4
}
```

Step 4 - Verify camera can see it:
```typescript
camera: {
  position: { x: 0, y: 2, z: 8 },  // Check this position
}
```

**If still invisible after all steps:**
- Dust render might be disabled (check no filter hiding it)
- Check GPU not failing (should see other objects)

---

### Issue: Scene Too Dark

**Symptoms:**
- Only see silhouettes
- Can't see model details
- Dust barely visible

**Quick Fix:**
```typescript
lighting: {
  keyLight: { intensity: 1.2 },      // Increase from 0.8
  fillLight: { intensity: 0.6 },     // Increase from 0.4
  ambientLight: { intensity: 0.7 },  // Increase from 0.5
}
```

**Or use preset:**
Change entire lighting section to:
```typescript
lighting: {
  keyLight: {
    color: 0xffffff,
    intensity: 1.2,  // Brighter
    position: { x: 5, y: 5, z: 5 },
  },
  fillLight: {
    color: 0xaaaaff,
    intensity: 0.6,  // Brighter
    position: { x: -3, y: 3, z: -5 },
  },
  rimLight: {
    color: 0xffaaaa,
    intensity: 0.5,  // Brighter
    position: { x: 0, y: 8, z: -10 },
  },
  ambientLight: {
    color: 0x333333,
    intensity: 0.8,  // Brighter
  },
}
```

---

### Issue: Scene Too Bright / Washed Out

**Symptoms:**
- Everything is white
- Can't see details
- Bloom effect overwhelming

**Quick Fix:**
```typescript
lighting: {
  keyLight: { intensity: 0.5 },      // Decrease from 0.8
  ambientLight: { intensity: 0.3 },  // Decrease from 0.5
}

bloom: {
  intensity: 0.5,  // Much lower
}
```

---

### Issue: Bloom/Glow Not Visible

**Symptoms:**
- No glow around particles or model
- Everything looks flat

**Check:**
```typescript
bloom: {
  enabled: true,  // Must be true
  intensity: 1.5,
}
```

**If already `enabled: true`:**
- Try increasing intensity:
```typescript
bloom: {
  intensity: 3.0,  // Much higher
  luminanceThreshold: 0.1,  // Lower threshold
}
```

---

### Issue: Clock Not Visible

**Symptoms:**
- Can see 3D scene but no clock in top-right
- No green text with time

**Check:**
1. Is text hidden off-screen?
   - Check browser window width (clock may be off to right)
   - Try widening browser window

2. Is text behind other elements?
   - Check CSS z-index
   - Console should show no DOM errors

3. Is text the wrong color?
   - Should be bright green (#00ff88)
   - Check against dark background

**If never appears:**
```typescript
// Verify this exists in timeManagerRef.current.createClockElement()
clock.style.cssText = `
  position: fixed;
  top: 20px;
  right: 20px;
  ...
`;
```

If missing, there's an error with TimeDisplayManager.

---

## 🟢 Performance Issues

### Issue: Low Frame Rate (< 30 FPS)

**Symptoms:**
- Animation stutters/jerky
- Dust moves in chunks, not smoothly
- Lag when dust updates

**Fix - Reduce Dust:**
```typescript
dust: {
  count: 1000,  // Reduce from 2000
}
```

**Fix - Reduce Bloom:**
```typescript
bloom: {
  intensity: 0.8,  // Reduce from 1.5
  enabled: false,  // Or disable entirely
}
```

**Fix - Reduce Scene Complexity:**
- Remove unnecessary lights (if added)
- Reduce model polygon count
- Use lower resolution textures

**Check Performance:**
1. Open DevTools → Performance tab
2. Start recording
3. Let run for 3 seconds
4. Stop recording
5. Look for consistent frame time < 16ms

---

### Issue: Memory Leak (Browser Gets Slower Over Time)

**Symptoms:**
- App works fine at start
- Gets slower over 10-20 minutes
- Computer becomes sluggish
- Task Manager shows increasing memory

**Root Causes:**
1. Old models not properly disposed
2. Textures not freed
3. Animation frame not properly cancelled

**Fix:**
Ensure cleanup is correct. In `ParticleFieldVanilla.tsx`, cleanup should:
```typescript
// Cancel animation frame
if (animationFrameRef.current) {
  cancelAnimationFrame(animationFrameRef.current);
}

// Clear intervals
if (clockIntervalRef.current) {
  clearInterval(clockIntervalRef.current);
}

// Dispose models/materials/geometry
modelManager.disposeModel(currentModel);
dustSystem.dispose();

// Dispose renderer
renderer.dispose();
composer.dispose();
```

If you modified code, ensure these are present.

---

### Issue: Model Swap Causes Frame Drops

**Symptoms:**
- Smooth animation
- 1-second pause when time changes to "13"
- Dust stops moving during swap

**Why:** Model loading is synchronous (blocking)

**Workaround:**
Can't fully fix without restructuring, but can minimize by:
- Using simpler models (fewer polygons)
- Reducing model file size
- Pre-caching models (if you have < 3)

---

## 🔵 Configuration Issues

### Issue: Changed Config But Nothing Happens

**Symptoms:**
- Edit `sceneConfig.ts`
- Dust count or lighting doesn't change
- Values ignored

**Fix:**
1. Make sure you saved the file
2. Stop dev server (Ctrl+C)
3. Restart dev server (npm run dev)
4. Hard refresh browser (Ctrl+Shift+R or Ctrl+Shift+Delete)

**If still not working:**
- Check you're editing the right sceneConfig.ts
- Check you're modifying the exported const:
  ```typescript
  export const sceneConfig = { ... }  // ✓ This one
  ```
- Check file has no syntax errors
  - Should see error in console if it has

---

### Issue: Wrong Monster Paths Not Working

**Symptoms:**
- Config points to `/models/monsters/monster01.glb`
- File actually at `/models/monsters/boss.glb`
- Monster won't load

**Fix:**
Update ALL paths to match actual files:
```typescript
monsters: [
  { path: "/models/monsters/boss.glb", scale: 1.5 },        // Changed
  { path: "/models/monsters/enemy.glb", scale: 1.8 },       // Changed
  { path: "/models/monsters/creature.glb", scale: 1.5 },    // Changed
],
```

**Verify by checking file explorer:**
```
public/models/monsters/
├── boss.glb          ← Check spelling
├── enemy.glb
└── creature.glb
```

---

## 🟣 Advanced Debugging

### Enable Console Logging

Add debug logs to ParticleFieldVanilla.tsx:

```typescript
// In animation loop:
if (frame % 60 === 0) {  // Log every second
  console.log('FPS:', 60, 'Particles:', dustSystem.count);
}

// In model manager:
console.log('Loading model:', path);
console.log('Model loaded successfully');
console.log('Model disposal complete');
```

### Check Browser Performance

1. Open DevTools
2. Performance tab
3. Start recording
4. Interact (trigger time change, etc.)
5. Stop recording
6. Analyze:
   - Look for red vertical lines (jank)
   - Each frame should be ~16ms max
   - GPU usage should be consistent

### Check Network

1. Open DevTools
2. Network tab
3. Refresh page
4. Should see:
   - `/models/teddy/modelA.glb` loaded (200 status)
   - No 404 errors
   - File size reasonable (< 10MB)

---

## 🆘 Still Not Working?

### Checklist Before Asking for Help

- [ ] Checked browser console for errors?
- [ ] Verified model files exist in public/models/?
- [ ] Verified config paths match file paths exactly?
- [ ] Restarted dev server and hard refreshed browser?
- [ ] Checked Next.js build completes without errors?
- [ ] Tried with simpler test model?
- [ ] Checked file permissions (readable)?
- [ ] Used `.glb` or `.gltf` files only?

### Debug Information to Collect

When asking for help, provide:
1. Exact error message from console
2. What you changed in config
3. What files you added to public/models/
4. Screenshot of your file structure
5. Steps to reproduce the issue

---

## 📚 Additional Resources

- Three.js Docs: https://threejs.org/docs/
- GLTF Format: https://www.khronos.org/gltf/
- postprocessing Docs: https://www.npmjs.com/package/postprocessing
- Blender Export GLB: https://docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html

---

**Most issues can be solved by:**
1. Checking console errors
2. Verifying file paths
3. Restarting dev server
4. Hard refreshing browser

Try those three steps first! ✅
