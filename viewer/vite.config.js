import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const serverPort = process.env.SCOPE_PORT || 6000
const clientPort = process.env.SCOPE_PORT_DEV || 8000

export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: clientPort,
    proxy: {
      '/api': {
        target: `http://127.0.0.1:${serverPort}`,
        changeOrigin: true,
        timeout: 60000,  // 1 min
      }
    }
  }
})
