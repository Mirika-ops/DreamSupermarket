declare module 'three/examples/jsm/loaders/FBXLoader' {
  import { Loader, LoadingManager } from 'three';
  export class FBXLoader extends Loader {
    constructor(manager?: LoadingManager);
    load(
      url: string,
      onLoad?: (object: any) => void,
      onProgress?: (event: ProgressEvent) => void,
      onError?: (event: ErrorEvent) => void
    ): Promise<any>;
    parse(
      arrayBuffer: ArrayBuffer,
      onParse: (geometry: any, materials: any[]) => void
    ): void;
  }
}

declare module 'three/examples/jsm/controls/OrbitControls' {
  import { Camera, MOUSE, Vector3 } from 'three';
  import { EventDispatcher } from 'three';
  export class OrbitControls extends EventDispatcher {
    constructor(camera: Camera, domElement: HTMLElement);
    autoRotate: boolean;
    autoRotateSpeed: number;
    damping: boolean;
    dampingFactor: number;
    enableDamping: boolean;
    enablePan: boolean;
    enableRotate: boolean;
    enableZoom: boolean;
    maxDistance: number;
    minDistance: number;
    object: Camera;
    target: Vector3;
    update(): void;
    dispose(): void;
    saveState(): void;
    reset(): void;
  }
}
