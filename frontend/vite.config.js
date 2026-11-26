import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// 前端开发端口 5173，与后端 CORS 放行地址一致
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
  },
})
