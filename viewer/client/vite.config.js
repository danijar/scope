import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
// import vueDevTools from 'vite-plugin-vue-devtools'

const clientPort = process.env.SCOPE_CLIENT_PORT || 8080
const serverPort = process.env.SCOPE_SERVER_PORT || 6008

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    // vueDevTools(),
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
        rewrite: (path) => path.replace(/^\/api/, ''),
        timeout: 60000,  // 1min
      }
    }
  }
})
