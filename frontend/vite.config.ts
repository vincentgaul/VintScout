/**
 * Vite Configuration File
 *
 * Vite is the build tool for our React frontend. This file configures how it works.
 *
 * What this file does:
 * - Sets up React plugin so Vite can handle React code
 * - Creates an alias '@' that points to the 'src' folder
 *   (so you can write: import { api } from '@/lib/api' instead of '../../lib/api')
 * - Configures the dev server to run on port 5173
 * - Sets up a proxy that forwards /api requests to the backend on port 3000
 *   (this avoids CORS issues during development)
 *
 * You usually don't need to modify this unless you're changing build settings.
 */

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: true,
      },
    },
  },
})
