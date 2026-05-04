/**
 * Scene Configuration
 * 
 * Centralized configuration for the 3D exhibition scene.
 * Modify these values to adjust models, particles, lighting, and more
 * without touching the core rendering logic.
 */

export const sceneConfig = {
  // ==================== SCENE SETUP ====================
  scene: {
    backgroundColor: 0x0a0a0a,        // Dark background color
    fogColor: 0x000000,
    fogNear: 1,
    fogFar: 50,
  },

  // ==================== CAMERA ====================
  camera: {
    fov: 75,
    position: { x: 0, y: 2, z: 8 },   // Camera looking at center from front
    lookAt: { x: 0, y: 1, z: 0 },     // Look at center of scene
  },

  // ==================== LIGHTING ====================
  lighting: {
    // Soft key light from above-front
    keyLight: {
      color: 0xffffff,
      intensity: 0.8,
      position: { x: 5, y: 5, z: 5 },
    },
    // Fill light from opposite side
    fillLight: {
      color: 0xaaaaff,               // Slight blue-ish fill for softness
      intensity: 0.4,
      position: { x: -3, y: 3, z: -5 },
    },
    // Rim light for subtle glow
    rimLight: {
      color: 0xffaaaa,               // Slight warm rim
      intensity: 0.3,
      position: { x: 0, y: 8, z: -10 },
    },
    // Ambient light for overall brightness
    ambientLight: {
      color: 0x333333,
      intensity: 0.5,
    },
  },

  // ==================== POST-PROCESSING ====================
  bloom: {
    enabled: true,
    intensity: 1.5,                   // Glow intensity
    luminanceThreshold: 0.3,          // Threshold for bloom
  },

  // ==================== DUST PARTICLE EFFECT ====================
  dust: {
    count: 2500,                      // Number of dust particles
    particleSize: 0.035,              // Particle size
    color: "#c8c8c8",                 // Dust color (light gray)
    opacity: 0.35,                    // Particle transparency
    
    // Physics parameters
    gravity: 0.0008,                  // Downward acceleration
    minFallSpeed: 0.002,              // Minimum particle fall speed
    maxFallSpeed: 0.008,              // Maximum particle fall speed
    windStrength: 0.004,              // Wind force magnitude
    windFrequency: 0.6,               // Wind oscillation frequency
    turbulence: 0.002,                // Random per-particle variation
    
    // Spawn volume - covers entire visible camera area
    spawnWidth: 8,                    // Width of spawn area (X axis)
    spawnDepth: 8,                    // Depth of spawn area (Z axis)
    respawnHeight: 5,                 // Y position where particles spawn
    floorOffsetBelowModel: 0.5,       // Offset below model bottom for floor
    floorY: -3,                       // Y position where particles respawn (updated per model)
  },

  // ==================== MODEL DISPLAY ====================
  models: {
    // Default teddy bear model (displayed when not in "13" trigger state)
    default: {
      path: "/models/teddy/Bear O.fbx",        // Path to teddy bear model
      scale: 0.01,                             // Scale multiplier (FBX files often need smaller scale)
      position: { x: 0, y: 0, z: 0 },         // Position in scene
      rotation: { x: 0, y: 0, z: 0 },         // Initial rotation (in radians)
    },
    
    // Monster models - one randomly selected when time string contains "13"
    // Examples that trigger: 13:XX:XX, XX:13:XX, XX:XX:13
    monsters: [
      { 
        path: "/models/monsters/Bear S.fbx", 
        scale: 0.01,
        position: { x: 0, y: 0, z: 0 },
        rotation: { x: 0, y: 0, z: 0 },
      },
      { 
        path: "/models/monsters/mannequin.fbx", 
        scale: 0.01,
        position: { x: 0, y: 0, z: 0 },
        rotation: { x: 0, y: 0, z: 0 },
      },
      { 
        path: "/models/monsters/mayfly.fbx", 
        scale: 0.01,
        position: { x: 0, y: 0, z: 0 },
        rotation: { x: 0, y: 0, z: 0 },
      },
    ],
  },

  // ==================== MODEL DISPLAY OPTIONS ====================
  modelDisplay: {
    autoCenter: true,                 // Automatically center model in viewport
    autoScale: true,                  // Automatically scale model to fit
    targetHeight: 2.8,                // Target model height in units
    manualScaleMultiplier: 1.2,       // Additional scale multiplier
    positionOffset: [0, 0.3, 0],      // Offset after centering
    rotationOffset: [0, 0, 0],        // Additional rotation (radians)
  },

  // ==================== RED UNDER LIGHT ====================
  redUnderLight: {
    enabled: true,                    // Enable/disable the red under light
    color: "#8b0000",                 // Dark red color
    intensity: 3,                     // Light intensity
    distance: 5,                      // Light distance/range
    decay: 2,                         // Light decay
    position: [0, -1.5, 0],           // Position below model
  },

  // ==================== MODEL SWAPPING TRIGGER ====================
  trigger: {
    // When current time (HH:mm:ss) contains the digit "13", swap to monster
    // Examples: 13:00:00, 01:13:22, 10:05:13 all trigger
    digit: "13",
    // Avoid model reloading - only swap when state changes
    // This is handled automatically in the code
  },

  // ==================== ORBIT CONTROLS ====================
  orbitControls: {
    enableDamping: true,              // Smooth camera movement
    dampingFactor: 0.05,              // Damping strength
    enableZoom: true,                 // Allow zoom with mouse wheel
    enableRotate: true,               // Allow rotation with mouse drag
    enablePan: false,                 // Disable panning
    autoRotate: false,                // Auto rotation (can be enabled for idle state)
    autoRotateSpeed: 2,               // Auto rotation speed if enabled
  },

  // ==================== EXTRA MONSTER SPAWNING (44-Second Interval) ====================
  extraMonsterSpawn: {
    enabled: true,                    // Enable/disable extra monster spawning
    intervalSeconds: 44,              // Spawn a monster every X seconds
    maxCount: 20,                     // Maximum number of extra monsters in scene
    spawnRangeX: 4,                   // Random X range: [-spawnRangeX, spawnRangeX]
    spawnRangeZ: 3,                   // Random Z range: [-spawnRangeZ, spawnRangeZ]
    avoidCenterRadius: 1.2,           // Avoid spawning within this radius of center
    scaleMultiplier: 1,               // Scale multiplier for extra monsters
    faceCenter: true,                 // Rotate extra monsters to face the center
  },

  // ==================== ANIMATION LOOP ====================
  animation: {
    enableAutoRotation: false,        // Rotate the model continuously
    rotationSpeed: 0.005,             // Model rotation speed (radians per frame)
  },

  // ==================== PROJECT INFORMATION ====================
  projectInfo: {
    title: "Consumables",    // Main project title - edit this
    concept: "Have you ever dreamed of an endless supermarket?",  // Motivation/concept description
    instructions: [
      "Drag / swipe to rotate the camera.",
      "Scroll / pinch to zoom.",
      "Observe the teddy bear in the dust-filled space.",
      "A random monster appears every 44 seconds.",
      "Refreshing the page resets the spawned monsters.",
    ],
    video: {
      enabled: true,
      localPath: "",  // Local video file (disabled)
      externalUrl: "https://www.youtube.com/embed/tGy3GEHmhvM",  // YouTube embed URL
    },
  },

  // ==================== RESPONSIVE SETTINGS ====================
  responsive: {
    // Reduce particles on mobile for better performance
    mobileParticleCountMultiplier: 0.5,  // Use 50% particles on mobile
    maxPixelRatio: 2,                     // Limit pixel ratio for performance
    touchControlsEnabled: true,           // Enable touch/two-finger zoom on mobile
  },
};

export default sceneConfig;
