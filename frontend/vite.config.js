import { defineConfig } from 'vite'

export default defineConfig({
  base: process.env.BASE_PATH || '/',
  esbuild: { jsx: 'automatic', jsxImportSource: 'react' },
  server: {
    host: 'localhost',
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes('node_modules')) return undefined
          if (id.includes('/recharts/') || id.includes('/d3-')) return 'charts'
          if (id.includes('/react/') || id.includes('/react-dom/') || id.includes('/react-router')) return 'react-vendor'
          return undefined
        },
      },
    },
  },
})
