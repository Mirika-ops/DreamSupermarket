#!/usr/bin/env node

/**
 * Model Compression Script (Simplified)
 * Applies Draco compression to GLB models via gltf-transform CLI
 * Usage: npx gltf-transform compress public/models/teddy/Bear\ O.glb ./bear-compressed.glb --compression draco
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const modelsDir = path.join(__dirname, 'public', 'models');
const teddy = path.join(modelsDir, 'teddy', 'Bear O.glb');

console.log(`\n📦 Compressing Teddy Bear model with Draco...\n`);

if (!fs.existsSync(teddy)) {
  console.error(`❌ Model not found: ${teddy}`);
  process.exit(1);
}

try {
  const beforeSize = fs.statSync(teddy).size;
  console.log(`Input file: ${path.basename(teddy)} (${(beforeSize / 1024 / 1024).toFixed(1)} MB)\n`);
  console.log(`⏳ Running Draco compression...`);

  // Run compression via CLI
  const tempOutput = teddy.replace('.glb', '.tmp.glb');
  execSync(
    `npx gltf-transform compress "${teddy}" "${tempOutput}" --compression draco`,
    { 
      stdio: 'inherit',
      shell: true
    }
  );

  if (fs.existsSync(tempOutput)) {
    fs.renameSync(tempOutput, teddy);
    const afterSize = fs.statSync(teddy).size;
    const reduction = ((1 - afterSize / beforeSize) * 100).toFixed(1);
    
    console.log(`\n✅ Compression successful!`);
    console.log(`Size: ${(beforeSize / 1024 / 1024).toFixed(2)} MB → ${(afterSize / 1024 / 1024).toFixed(2)} MB`);
    console.log(`Reduction: ${reduction}%\n`);
  }
} catch (error) {
  console.error(`\n⚠️  Note: gltf-transform CLI may not be installed globally.`);
  console.error(`Install with: npm install -g @gltf-transform/cli`);
  console.error(`Error: ${error.message}\n`);
}
