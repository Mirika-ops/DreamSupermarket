'use client';

import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
// @ts-ignore
import { FBXLoader } from 'three/examples/jsm/loaders/FBXLoader';
// @ts-ignore
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { EffectComposer, RenderPass, EffectPass, BloomEffect } from 'postprocessing';
import { sceneConfig } from '../sceneConfig';

/**
 * Helper: Create circular dust particle texture
 * Returns a canvas texture with a circular gradient for soft dust particles
 */
function createCircleTexture(): THREE.Texture {
  const canvas = document.createElement('canvas');
  canvas.width = 64;
  canvas.height = 64;
  
  const ctx = canvas.getContext('2d');
  if (!ctx) return new THREE.Texture();
  
  // Clear canvas
  ctx.clearRect(0, 0, 64, 64);
  
  // Create radial gradient (soft circle)
  const grad = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
  grad.addColorStop(0, 'rgba(255, 255, 255, 1)');
  grad.addColorStop(0.5, 'rgba(255, 255, 255, 0.8)');
  grad.addColorStop(1, 'rgba(255, 255, 255, 0)');
  
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 64, 64);
  
  const texture = new THREE.CanvasTexture(canvas);
  texture.needsUpdate = true;
  return texture;
}

/**
 * Helper: Fit and center a model in the viewport
 * Computes bounding box, centers it, and scales to target height
 */
function fitModelToView(model: THREE.Group, config: any): void {
  const box = new THREE.Box3().setFromObject(model);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  
  // Move to origin
  model.position.sub(center);
  
  // Scale to target height
  if (config.modelDisplay.autoScale && size.y > 0) {
    const scale = config.modelDisplay.targetHeight / size.y;
    model.scale.multiplyScalar(scale);
    model.scale.multiplyScalar(config.modelDisplay.manualScaleMultiplier);
  }
  
  // Apply position offset
  const offset = config.modelDisplay.positionOffset;
  model.position.add(new THREE.Vector3(offset[0], offset[1], offset[2]));
  
  // Apply rotation offset
  const rotOffset = config.modelDisplay.rotationOffset;
  model.rotation.x += rotOffset[0];
  model.rotation.y += rotOffset[1];
  model.rotation.z += rotOffset[2];
}

/**
 * Helper: Get model bounding box and calculate bounds
 * Returns bounding box info including center and dimensions
 */
function getModelBounds(model: THREE.Group): { box: THREE.Box3; center: THREE.Vector3; size: THREE.Vector3 } {
  const box = new THREE.Box3().setFromObject(model);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  return { box, center, size };
}

/**
 * Helper: Setup OrbitControls for interactive camera movement
 */
function setupOrbitControls(camera: THREE.PerspectiveCamera, renderer: THREE.WebGLRenderer, config: any): OrbitControls {
  const controls = new OrbitControls(camera, renderer.domElement);
  
  controls.enableDamping = config.orbitControls.enableDamping;
  controls.dampingFactor = config.orbitControls.dampingFactor;
  controls.enableZoom = config.orbitControls.enableZoom;
  controls.enableRotate = config.orbitControls.enableRotate;
  controls.enablePan = config.orbitControls.enablePan;
  controls.autoRotate = config.orbitControls.autoRotate;
  controls.autoRotateSpeed = config.orbitControls.autoRotateSpeed;
  
  // Set reasonable viewing distance
  controls.minDistance = 2;
  controls.maxDistance = 20;
  
  controls.update();
  
  return controls;
}

/**
 * Helper: Update controls target to focus on model center
 */
function updateControlsTarget(controls: OrbitControls, model: THREE.Group): void {
  const bounds = getModelBounds(model);
  controls.target.copy(bounds.center);
  controls.update();
}

/**
 * Helper: Calculate dust floor based on model bounds
 * Particles should fall below the lowest point of the model
 */
function updateDustFloorFromModel(model: THREE.Group, config: any): number {
  const bounds = getModelBounds(model);
  const offset = config.dust.floorOffsetBelowModel || 0.5;
  return bounds.box.min.y - offset; // Place floor below model bottom
}

/**
 * Helper: Get random spawn position for extra monster (away from center)
 */
function getRandomMonsterSpawnPosition(modelBottomY: number, config: any): THREE.Vector3 {
  const spawnRangeX = config.extraMonsterSpawn.spawnRangeX || 4;
  const spawnRangeZ = config.extraMonsterSpawn.spawnRangeZ || 3;
  const avoidRadius = config.extraMonsterSpawn.avoidCenterRadius || 1.2;

  // Random X position, avoiding the center area
  let x = Math.random() * (spawnRangeX * 2) - spawnRangeX;
  if (Math.abs(x) < avoidRadius) {
    x += x < 0 ? -avoidRadius - 0.5 : avoidRadius + 0.5;
  }

  // Random Z position
  const z = Math.random() * (spawnRangeZ * 2) - spawnRangeZ;

  return new THREE.Vector3(x, modelBottomY, z);
}

/**
 * Helper: Create and add extra monster to scene
 */
function createExtraMonster(
  modelPath: string,
  position: THREE.Vector3,
  scale: number,
  fbxLoader: FBXLoader,
  config: any
): Promise<THREE.Group | null> {
  return new Promise((resolve) => {
    fbxLoader.load(
      modelPath,
      (model: THREE.Group) => {
        // Apply scale
        model.scale.multiplyScalar(scale * config.extraMonsterSpawn.scaleMultiplier);

        // Set position
        model.position.copy(position);

        // Optionally face the center
        if (config.extraMonsterSpawn.faceCenter) {
          const direction = new THREE.Vector3(0, 0, 0).sub(position).normalize();
          const angle = Math.atan2(direction.x, direction.z);
          model.rotation.y = angle;
        }

        resolve(model);
      },
      undefined,
      (error: any) => {
        console.error(`Error loading extra monster ${modelPath}:`, error);
        resolve(null);
      }
    );
  });
}

/**
 * Dust Particle System
 * 
 * Creates and manages falling dust particles with gravity, wind, and turbulence.
 * Particles spawn at the top and fall downward, respawning when they exit the bottom.
 */
class DustParticleSystem {
  particles: Float32Array;
  velocities: Float32Array;
  windPhases: Float32Array;
  count: number;
  geometry: THREE.BufferGeometry;
  material: THREE.PointsMaterial;
  mesh: THREE.Points;
  time: number = 0;
  windTime: number = 0;

  constructor(count: number, config: any) {
    this.count = count;

    // Initialize particle data
    this.particles = new Float32Array(count * 3);
    this.velocities = new Float32Array(count * 3);
    this.windPhases = new Float32Array(count);

    // Create geometry
    this.geometry = new THREE.BufferGeometry();
    this.geometry.setAttribute('position', new THREE.BufferAttribute(this.particles, 3));

    // Create circular texture for dust
    const circleTexture = createCircleTexture();

    // Create material with circular texture
    this.material = new THREE.PointsMaterial({
      map: circleTexture,
      color: config.dust.color,
      size: config.dust.particleSize,
      transparent: true,
      opacity: config.dust.opacity,
      sizeAttenuation: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });

    // Create mesh
    this.mesh = new THREE.Points(this.geometry, this.material);

    // Initialize particles
    this.resetParticles(config);
  }

  private resetParticle(index: number, config: any): void {
    const spawnWidth = config.dust.spawnWidth || 8;
    const spawnDepth = config.dust.spawnDepth || 8;
    const minFallSpeed = config.dust.minFallSpeed || 0.002;
    const maxFallSpeed = config.dust.maxFallSpeed || 0.008;

    // Random spawn position across the entire visible camera area
    this.particles[index * 3] = (Math.random() - 0.5) * spawnWidth;
    this.particles[index * 3 + 1] = config.dust.respawnHeight * (0.8 + Math.random() * 0.2);
    this.particles[index * 3 + 2] = (Math.random() - 0.5) * spawnDepth;

    // Random initial velocities
    this.velocities[index * 3] = (Math.random() - 0.5) * 0.02;
    this.velocities[index * 3 + 1] = -Math.random() * (maxFallSpeed - minFallSpeed) - minFallSpeed;
    this.velocities[index * 3 + 2] = (Math.random() - 0.5) * 0.02;

    // Random wind phase per particle for natural variation
    this.windPhases[index] = Math.random() * Math.PI * 2;
  }

  private resetParticles(config: any): void {
    for (let i = 0; i < this.count; i++) {
      this.resetParticle(i, config);
    }
  }

  update(deltaTime: number, config: any): void {
    this.time += deltaTime;
    this.windTime += deltaTime;
    let posChanged = false;

    for (let i = 0; i < this.count; i++) {
      const idx = i * 3;

      // Apply gravity (downward acceleration)
      this.velocities[idx + 1] -= config.dust.gravity * deltaTime;

      // Wind force (sinusoidal variation with per-particle phase offset)
      const windPhase = this.windTime * config.dust.windFrequency + this.windPhases[i];
      const windForce = Math.sin(windPhase) * config.dust.windStrength;
      this.velocities[idx] += windForce * deltaTime;
      
      // Random turbulence per particle
      const turbulence = Math.sin(this.time * 0.3 + i * 0.01) * config.dust.turbulence;
      this.velocities[idx] += turbulence * deltaTime;

      // Apply velocity to position
      this.particles[idx] += this.velocities[idx] * deltaTime;
      this.particles[idx + 1] += this.velocities[idx + 1] * deltaTime;
      this.particles[idx + 2] += this.velocities[idx + 2] * deltaTime;

      // Respawn individual particles that fall below floor
      if (this.particles[idx + 1] < config.dust.floorY) {
        this.resetParticle(i, config);
        posChanged = true;
      }
    }

    // Update GPU buffer
    this.geometry.attributes.position.needsUpdate = true;
  }

  dispose(): void {
    this.geometry.dispose();
    this.material.dispose();
    if (this.material.map) this.material.map.dispose();
  }
}

/**
 * Model Manager
 * 
 * Handles loading, caching, and disposal of FBX models.
 * Automatically disposes old models when switching.
 */
class ModelManager {
  fbxLoader: FBXLoader;
  currentModel: THREE.Group | null = null;
  modelCache: Map<string, THREE.Group> = new Map();

  constructor() {
    this.fbxLoader = new FBXLoader();
  }

  async loadModel(modelPath: string): Promise<THREE.Group> {
    // Check cache first
    if (this.modelCache.has(modelPath)) {
      console.log(`Loading model from cache: ${modelPath}`);
      return this.modelCache.get(modelPath)!.clone();
    }

    console.log(`Loading model: ${modelPath}`);
    return new Promise((resolve, reject) => {
      this.fbxLoader.load(
        modelPath,
        (scene: THREE.Group) => {
          this.modelCache.set(modelPath, scene);
          resolve(scene);
        },
        undefined,
        (error: any) => {
          console.error(`Error loading model ${modelPath}:`, error);
          reject(error);
        }
      );
    });
  }

  disposeModel(model: THREE.Group) {
    model.traverse((child) => {
      if ((child as THREE.Mesh).geometry) {
        (child as THREE.Mesh).geometry.dispose();
      }
      if ((child as THREE.Mesh).material) {
        const mats = (child as THREE.Mesh).material;
        const materials: any[] = Array.isArray(mats) ? mats : [mats];
        materials.forEach((material: any) => {
          material.dispose();
        });
      }
    });
  }

  async setModel(
    parent: THREE.Scene,
    modelPath: string,
    scale: number,
    position: THREE.Vector3,
    config: any
  ) {
    // Dispose old model
    if (this.currentModel) {
      this.disposeModel(this.currentModel);
      parent.remove(this.currentModel);
    }

    // Load new model
    const model = await this.loadModel(modelPath);
    model.scale.set(scale, scale, scale);
    model.position.copy(position);

    // Apply auto-centering and scaling if enabled
    if (config.modelDisplay.autoCenter || config.modelDisplay.autoScale) {
      fitModelToView(model, config);
    } else {
      // Apply only rotation offset if no auto-centering
      const rotOffset = config.modelDisplay.rotationOffset;
      model.rotation.x += rotOffset[0];
      model.rotation.y += rotOffset[1];
      model.rotation.z += rotOffset[2];
    }

    parent.add(model);
    this.currentModel = model;
  }

  clearCache() {
    this.modelCache.forEach((model) => {
      this.disposeModel(model);
    });
    this.modelCache.clear();
  }
}

/**
 * Time Display Manager
 * 
 * Manages digital clock display and trigger logic.
 * Checks if current time contains "13" to trigger monster display.
 */
class TimeDisplayManager {
  clockElement: HTMLElement | null = null;
  currentTime: string = '';

  createClockElement(): HTMLElement {
    const clock = document.createElement('div');
    clock.id = 'digital-clock';
    clock.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      font-family: 'Courier New', monospace;
      font-size: 32px;
      font-weight: bold;
      color: #00ff88;
      background: rgba(0, 0, 0, 0.7);
      padding: 15px 25px;
      border-radius: 8px;
      border: 2px solid #00ff88;
      z-index: 1000;
      text-shadow: 0 0 10px #00ff88;
      letter-spacing: 2px;
    `;
    clock.textContent = '00:00:00';
    document.body.appendChild(clock);
    this.clockElement = clock;
    return clock;
  }

  update(): string {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');

    this.currentTime = `${hours}:${minutes}:${seconds}`;

    if (this.clockElement) {
      this.clockElement.textContent = this.currentTime;
    }

    return this.currentTime;
  }

  cleanup() {
    if (this.clockElement && this.clockElement.parentNode) {
      this.clockElement.parentNode.removeChild(this.clockElement);
    }
  }
}

/**
 * Main Particle Field Component
 * 
 * Sets up a dark exhibition scene with:
 * - Circular dust particles with gravity and wind
 * - Model display (teddy bear or random monster)
 * - Soft lighting with red under-light
 * - Time-based trigger logic
 * - Beautiful bloom post-processing
 */
export default function ParticleFieldVanilla() {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const composerRef = useRef<EffectComposer | null>(null);
  const dustSystemRef = useRef<DustParticleSystem | null>(null);
  const modelManagerRef = useRef<ModelManager | null>(null);
  const controlsRef = useRef<OrbitControls | null>(null);
  const timeManagerRef = useRef<TimeDisplayManager | null>(null);
  const extraMonstersRef = useRef<THREE.Group[]>([]);
  const lastMonsterSpawnTimeRef = useRef<number>(0);
  const animationFrameRef = useRef<number | null>(null);
  const clockIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!containerRef.current) return;

    // Initialize scene, camera, renderer
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(sceneConfig.scene.backgroundColor);
    scene.fog = new THREE.Fog(
      sceneConfig.scene.fogColor,
      sceneConfig.scene.fogNear,
      sceneConfig.scene.fogFar
    );
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(
      sceneConfig.camera.fov,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    camera.position.set(
      sceneConfig.camera.position.x,
      sceneConfig.camera.position.y,
      sceneConfig.camera.position.z
    );
    camera.lookAt(
      sceneConfig.camera.lookAt.x,
      sceneConfig.camera.lookAt.y,
      sceneConfig.camera.lookAt.z
    );
    cameraRef.current = camera;

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    containerRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // ==================== ORBIT CONTROLS ====================
    const controls = setupOrbitControls(camera, renderer, sceneConfig);
    controlsRef.current = controls;

    // ==================== LIGHTING ====================
    // Key light
    const keyLight = new THREE.DirectionalLight(
      sceneConfig.lighting.keyLight.color,
      sceneConfig.lighting.keyLight.intensity
    );
    keyLight.position.set(
      sceneConfig.lighting.keyLight.position.x,
      sceneConfig.lighting.keyLight.position.y,
      sceneConfig.lighting.keyLight.position.z
    );
    scene.add(keyLight);

    // Fill light
    const fillLight = new THREE.DirectionalLight(
      sceneConfig.lighting.fillLight.color,
      sceneConfig.lighting.fillLight.intensity
    );
    fillLight.position.set(
      sceneConfig.lighting.fillLight.position.x,
      sceneConfig.lighting.fillLight.position.y,
      sceneConfig.lighting.fillLight.position.z
    );
    scene.add(fillLight);

    // Rim light
    const rimLight = new THREE.DirectionalLight(
      sceneConfig.lighting.rimLight.color,
      sceneConfig.lighting.rimLight.intensity
    );
    rimLight.position.set(
      sceneConfig.lighting.rimLight.position.x,
      sceneConfig.lighting.rimLight.position.y,
      sceneConfig.lighting.rimLight.position.z
    );
    scene.add(rimLight);

    // Ambient light
    const ambientLight = new THREE.AmbientLight(
      sceneConfig.lighting.ambientLight.color,
      sceneConfig.lighting.ambientLight.intensity
    );
    scene.add(ambientLight);

    // ==================== RED UNDER LIGHT ====================
    if (sceneConfig.redUnderLight.enabled) {
      const redLight = new THREE.PointLight(
        sceneConfig.redUnderLight.color,
        sceneConfig.redUnderLight.intensity,
        sceneConfig.redUnderLight.distance
      );
      redLight.decay = sceneConfig.redUnderLight.decay;
      redLight.position.set(
        sceneConfig.redUnderLight.position[0],
        sceneConfig.redUnderLight.position[1],
        sceneConfig.redUnderLight.position[2]
      );
      scene.add(redLight);
    }

    // ==================== DUST PARTICLE SYSTEM ====================
    const dustSystem = new DustParticleSystem(
      sceneConfig.dust.count,
      sceneConfig
    );
    scene.add(dustSystem.mesh);
    dustSystemRef.current = dustSystem;

    // ==================== POST-PROCESSING (BLOOM) ====================
    const composer = new EffectComposer(renderer);
    const renderPass = new RenderPass(scene, camera);
    composer.addPass(renderPass);

    if (sceneConfig.bloom.enabled) {
      const bloomEffect = new BloomEffect({
        intensity: sceneConfig.bloom.intensity,
        luminanceThreshold: sceneConfig.bloom.luminanceThreshold,
        luminanceSmoothing: 0.025,
        mipmapBlur: true,
        resolutionX: window.innerWidth * window.devicePixelRatio,
        resolutionY: window.innerHeight * window.devicePixelRatio,
      });
      const effectPass = new EffectPass(camera, bloomEffect);
      composer.addPass(effectPass);
    }

    composerRef.current = composer;

    // ==================== MODEL MANAGER & TIME DISPLAY ====================
    const modelManager = new ModelManager();
    modelManagerRef.current = modelManager;

    const timeManager = new TimeDisplayManager();
    timeManager.createClockElement();
    timeManagerRef.current = timeManager;

    // Load default teddy bear model (central model - does not change)
    (async () => {
      await modelManager.setModel(
        scene,
        sceneConfig.models.default.path,
        sceneConfig.models.default.scale,
        new THREE.Vector3(
          sceneConfig.models.default.position.x,
          sceneConfig.models.default.position.y,
          sceneConfig.models.default.position.z
        ),
        sceneConfig
      );
      
      // Update camera controls to focus on the model
      if (controlsRef.current && modelManager.currentModel) {
        updateControlsTarget(controlsRef.current, modelManager.currentModel);
        // Update dust floor based on model bounds
        sceneConfig.dust.floorY = updateDustFloorFromModel(modelManager.currentModel, sceneConfig);
      }
      
      setIsLoading(false);
    })();

    // Clock display update loop (every 100ms) - visual only, no triggers
    clockIntervalRef.current = setInterval(() => {
      timeManager.update();
    }, 100);

    // ==================== ANIMATION LOOP ====================
    let lastTime = Date.now();
    let elapsedSeconds = 0;

    const animate = () => {
      animationFrameRef.current = requestAnimationFrame(animate);

      const currentTime = Date.now();
      const deltaTime = (currentTime - lastTime) / 1000; // Convert to seconds
      lastTime = currentTime;
      elapsedSeconds += deltaTime;

      // Clamp deltaTime to prevent large jumps
      const clampedDeltaTime = Math.min(deltaTime, 0.016);

      // Update dust particles
      if (dustSystem) {
        dustSystem.update(clampedDeltaTime, sceneConfig);
      }

      // Update camera controls
      if (controlsRef.current) {
        controlsRef.current.update();
      }

      // ==================== 44-SECOND MONSTER SPAWNER ====================
      if (sceneConfig.extraMonsterSpawn.enabled && modelManager.currentModel) {
        const spawnInterval = sceneConfig.extraMonsterSpawn.intervalSeconds || 44;

        if (elapsedSeconds - lastMonsterSpawnTimeRef.current >= spawnInterval) {
          lastMonsterSpawnTimeRef.current = elapsedSeconds;

          // Get the central model's bottom Y position for consistent placement
          const bounds = getModelBounds(modelManager.currentModel);
          const modelBottomY = bounds.box.min.y;

          // Get random spawn position
          const spawnPos = getRandomMonsterSpawnPosition(modelBottomY, sceneConfig);

          // Select random monster model
          const monsters = sceneConfig.models.monsters;
          const randomMonster = monsters[Math.floor(Math.random() * monsters.length)];

          // Create and add extra monster to scene (non-async version)
          modelManagerRef.current!.fbxLoader.load(
            randomMonster.path,
            (model: THREE.Group) => {
              // Apply scale
              model.scale.multiplyScalar(randomMonster.scale * sceneConfig.extraMonsterSpawn.scaleMultiplier);

              // Set position
              model.position.copy(spawnPos);

              // Optionally face the center
              if (sceneConfig.extraMonsterSpawn.faceCenter) {
                const direction = new THREE.Vector3(0, 0, 0).sub(spawnPos).normalize();
                const angle = Math.atan2(direction.x, direction.z);
                model.rotation.y = angle;
              }

              scene.add(model);
              extraMonstersRef.current.push(model);

              // Enforce max count limit
              if (extraMonstersRef.current.length > sceneConfig.extraMonsterSpawn.maxCount) {
                const oldMonster = extraMonstersRef.current.shift();
                if (oldMonster) {
                  modelManagerRef.current?.disposeModel(oldMonster);
                  scene.remove(oldMonster);
                }
              }

              console.log(`Spawned extra monster ${extraMonstersRef.current.length} at (${spawnPos.x.toFixed(1)}, ${spawnPos.y.toFixed(1)}, ${spawnPos.z.toFixed(1)})`);
            },
            undefined,
            (error: any) => {
              console.error(`Error loading extra monster ${randomMonster.path}:`, error);
            }
          );
        }
      }

      // Optional: Auto-rotate model
      if (
        sceneConfig.animation.enableAutoRotation &&
        modelManager.currentModel
      ) {
        modelManager.currentModel.rotation.y +=
          sceneConfig.animation.rotationSpeed;
      }

      // Render
      if (composer && composerRef.current) {
        composer.render();
      } else if (renderer) {
        renderer.render(scene, camera);
      }
    };

    animate();

    // ==================== WINDOW RESIZE ====================
    const handleResize = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;

      camera.aspect = width / height;
      camera.updateProjectionMatrix();

      renderer.setSize(width, height);
      composer.setSize(width, height);
    };

    window.addEventListener('resize', handleResize);

    // ==================== CLEANUP ====================
    return () => {
      window.removeEventListener('resize', handleResize);

      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }

      if (clockIntervalRef.current) {
        clearInterval(clockIntervalRef.current);
      }

      if (controlsRef.current) {
        controlsRef.current.dispose();
      }

      if (timeManager) {
        timeManager.cleanup();
      }

      if (dustSystem) {
        dustSystem.dispose();
      }

      if (modelManager && modelManager.currentModel) {
        modelManager.disposeModel(modelManager.currentModel);
      }

      // Dispose all extra monsters
      if (extraMonstersRef.current.length > 0 && modelManager) {
        extraMonstersRef.current.forEach((monster) => {
          modelManager.disposeModel(monster);
          scene.remove(monster);
        });
        extraMonstersRef.current = [];
      }

      if (renderer && containerRef.current && renderer.domElement.parentNode) {
        containerRef.current.removeChild(renderer.domElement);
      }

      // Dispose Three.js resources
      composerRef.current?.dispose();
      rendererRef.current?.dispose();
    };
  }, []);

  return (
    <div
      ref={containerRef}
      style={{
        width: '100vw',
        height: '100vh',
        overflow: 'hidden',
        margin: 0,
        padding: 0,
      }}
    >
      {isLoading && (
        <div
          style={{
            position: 'fixed',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            color: '#00ff88',
            fontSize: '24px',
            fontFamily: 'monospace',
            zIndex: 2000,
            textShadow: '0 0 10px #00ff88',
          }}
        >
          Loading exhibition...
        </div>
      )}
    </div>
  );
}
