#!/usr/bin/env node

/**
 * Model Compression Script
 * Applies Draco compression to all GLB models in public/models directory
 * Usage: node compress-models.js
 * 
 * Note: Draco compression CLI via gltf-transform
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

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

  for (const filepath of files) {
    const filename = path.basename(filepath);
    const outputPath = filepath.replace('.glb', '.compressed.glb');

    try {
      const beforeSize = fs.statSync(filepath).size;
      console.log(`⏳ Compressing: ${filename} (${(beforeSize / 1024 / 1024).toFixed(1)} MB)`);

      // Use gltf-transform CLI to compress with Draco
      try {
        execSync(
          `gltf-transform compress "${filepath}" "${outputPath}" --compression draco`,
          { stdio: 'pipe' }
        );

        // Replace original with compressed version
        fs.renameSync(outputPath, filepath);

        const afterSize = fs.statSync(filepath).size;
        const reduction = ((1 - afterSize / beforeSize) * 100).toFixed(1);

        console.log(`✅ ${filename}`);
        console.log(`   Size: ${(beforeSize / 1024 / 1024).toFixed(2)} MB → ${(afterSize / 1024 / 1024).toFixed(2)} MB`);
        console.log(`   Reduction: ${reduction}%\n`);
      } catch (execError) {
        // Fallback: File may be too small or already compressed
        console.warn(`⚠️  Skipped ${filename} (file may be empty or tool unavailable)\n`);
      }
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
});
