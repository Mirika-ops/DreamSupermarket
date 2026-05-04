/**
 * Type definitions for the Exhibition Scene
 * 
 * Use these types for enhanced IDE autocompletion and type safety.
 */

export interface Vector3Config {
  x: number;
  y: number;
  z: number;
}

export interface ColorConfig {
  color: number;
  intensity: number;
  position?: Vector3Config;
}

export interface DustConfig {
  count: number;
  color: number;
  size: number;
  opacity: number;
  fallSpeed: number;
  horizontalDriftSpeed: number;
  turbulenceAmount: number;
  spawnAreaX: number;
  spawnAreaZ: number;
  spawnHeight: number;
  respawnThreshold: number;
}

export interface ModelConfig {
  path: string;
  scale: number;
  position?: Vector3Config;
  rotation?: Vector3Config;
}

export interface LightingConfig {
  keyLight: ColorConfig;
  fillLight: ColorConfig;
  rimLight: ColorConfig;
  ambientLight: Omit<ColorConfig, 'position'>;
}

export interface SceneConfig {
  scene: {
    backgroundColor: number;
    fogColor: number;
    fogNear: number;
    fogFar: number;
  };
  camera: {
    fov: number;
    position: Vector3Config;
    lookAt: Vector3Config;
  };
  lighting: LightingConfig;
  bloom: {
    enabled: boolean;
    intensity: number;
    luminanceThreshold: number;
  };
  dust: DustConfig;
  models: {
    default: ModelConfig;
    monsters: Omit<ModelConfig, 'position' | 'rotation'>[];
  };
  trigger: {
    digit: string;
  };
  animation: {
    enableAutoRotation: boolean;
    rotationSpeed: number;
  };
}
