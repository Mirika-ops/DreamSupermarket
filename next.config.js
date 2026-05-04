/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable React strict mode for development
  reactStrictMode: true,
  
  // Optimize images
  images: {
    unoptimized: true, // Allow public directory images
  },
  
  // Allow loading models from public folder
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      "@": ["./src"],
    };
    return config;
  },
};

module.exports = nextConfig;
