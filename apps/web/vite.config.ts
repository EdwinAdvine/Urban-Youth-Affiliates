import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { visualizer } from 'rollup-plugin-visualizer'
import viteCompression from 'vite-plugin-compression'
import path from 'path'
import dotenv from 'dotenv'

dotenv.config()

export default defineConfig({
  plugins: [
    react(),
    visualizer({
      filename: 'dist/stats.html',
      gzipSize: true,
      brotliSize: true,
      open: false,
    }) as unknown as import('vite').Plugin,
    viteCompression({ algorithm: 'brotliCompress', ext: '.br', threshold: 1024 }),
    viteCompression({ algorithm: 'gzip', ext: '.gz', threshold: 1024 }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    target: 'es2020',
    chunkSizeWarningLimit: 500,
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          'vendor-state': ['zustand'],
          'vendor-ui': ['framer-motion', 'lucide-react'],
          'vendor-charts': ['recharts'],
        },
      },
    },
    cssCodeSplit: true,
    minify: 'esbuild',
    sourcemap: process.env.NODE_ENV !== 'production',
  },
  server: {
    port: parseInt(process.env.VITE_PORT || '3000'),
    host: true,
    open: true,
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
