#!/usr/bin/env node

/**
 * Model Compression Script
 * Applies Draco compression to all GLB models in public/models directory
 * Usage: node compress-models.js
 */

const fs = require('fs');
const path = require('path');
const { NodeIO } = require('@gltf-transform/core');
const { draco } = require('@gltf-transform/extensions');
const draco3d = require('draco3d');

// Initialize Draco encoder
const dracoEncoder = draco3d.createEncoderModule({});

async function compressModels() {
  const modelsDir = path.join(__dirname, 'public', 'models');
  const files = [];

  // Recursively find all GLB files
  function walkDir(dir) {
    const items = fs.readdirSync(dir);
    items.forEach(item => {
      const fullPath = path.join(dir, item);
      const stat = fs.statSync(fullPath);
      if (stat.isDirectory()) {
        walkDir(fullPath);
      } else if (item.endsWith('.glb')) {
        files.push(fullPath);
      }
    });
  }

  walkDir(modelsDir);

  if (files.length === 0) {
    console.log('No GLB files found in public/models');
    return;
  }

  console.log(`\n📦 Compressing ${files.length} model(s) with Draco...\n`);

  const io = new NodeIO();

  for (const filepath of files) {
    const filename = path.basename(filepath);
    const relativePath = path.relative(__dirname, filepath);

    try {
      const beforeSize = fs.statSync(filepath).size;
      console.log(`⏳ Compressing: ${filename}`);

      // Read GLB
      const document = await io.read(filepath);

      // Apply Draco compression
      await document.transform(
        draco(dracoEncoder, {
          method: 1, // 0 = edgebreaker, 1 = sequential
          quantizePosition: 12,
          quantizeNormal: 10,
          quantizeTexcoord: 12,
          quantizeColor: 8,
          quantizeGeneric: 12,
          quantizationOrigin: [0, 0, 0],
        })
      );

      // Write compressed GLB
      await io.write(filepath, document);

      const afterSize = fs.statSync(filepath).size;
      const reduction = ((1 - afterSize / beforeSize) * 100).toFixed(1);

      console.log(`✅ ${filename}`);
      console.log(`   Size: ${(beforeSize / 1024).toFixed(2)} KB → ${(afterSize / 1024).toFixed(2)} KB`);
      console.log(`   Reduction: ${reduction}%\n`);
    } catch (error) {
      console.error(`❌ Failed to compress ${filename}:`, error.message);
    }
  }

  console.log('✨ Compression complete!');
}

compressModels().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
