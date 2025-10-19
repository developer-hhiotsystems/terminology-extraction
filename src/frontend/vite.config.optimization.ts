import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { visualizer } from 'rollup-plugin-visualizer'
import compression from 'vite-plugin-compression'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),

    // Gzip compression
    compression({
      algorithm: 'gzip',
      ext: '.gz',
      threshold: 10240, // Only compress files larger than 10KB
    }),

    // Brotli compression (better than gzip)
    compression({
      algorithm: 'brotliCompress',
      ext: '.br',
      threshold: 10240,
    }),

    // Bundle analyzer (run with ANALYZE=true)
    visualizer({
      open: process.env.ANALYZE === 'true',
      filename: 'dist/stats.html',
      gzipSize: true,
      brotliSize: true,
    }),
  ],

  build: {
    // Target modern browsers
    target: 'es2015',

    // Output directory
    outDir: 'dist',

    // Generate source maps for production (set to false for smaller bundles)
    sourcemap: process.env.NODE_ENV === 'development',

    // Minification
    minify: 'terser',
    terserOptions: {
      compress: {
        // Remove console.log in production
        drop_console: process.env.NODE_ENV === 'production',
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.info'],
      },
      format: {
        comments: false, // Remove comments
      },
    },

    // Chunk size warnings
    chunkSizeWarningLimit: 500, // KB

    // Rollup options
    rollupOptions: {
      output: {
        // Manual chunk splitting for better caching
        manualChunks: {
          // React vendor chunk
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],

          // D3.js chunk (large library)
          'd3-vendor': ['d3'],

          // UI components chunk
          'ui-components': [
            './src/components/SearchBar.tsx',
            './src/components/SearchResults.tsx',
            './src/components/AdvancedSearch.tsx',
          ],

          // Graph visualization chunk (lazy load)
          'graph': [
            './src/components/GraphVisualization.tsx',
            './src/components/RelationshipExplorer.tsx',
          ],
        },

        // Asset file names
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.')
          const ext = info[info.length - 1]

          // Organize by type
          if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(ext)) {
            return `assets/images/[name]-[hash][extname]`
          } else if (/woff2?|ttf|eot/i.test(ext)) {
            return `assets/fonts/[name]-[hash][extname]`
          }

          return `assets/[name]-[hash][extname]`
        },

        // Chunk file names
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
      },
    },

    // CSS code splitting
    cssCodeSplit: true,
  },

  // Optimize dependencies
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom'],
    exclude: ['@vite/client', '@vite/env'],
  },

  // Server configuration
  server: {
    port: 3000,
    strictPort: false,

    // HMR configuration
    hmr: {
      overlay: true,
    },
  },

  // Preview server (production preview)
  preview: {
    port: 3000,
    strictPort: false,
  },
})
