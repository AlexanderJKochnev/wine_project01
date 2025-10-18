// vite.config.ts
import { defineConfig } from 'vite';
import preact from '@preact/preset-vite';

export default defineConfig({
  plugins: [preact()],
  resolve: {
    alias: {
      'react': 'preact/compat',
      'react-dom': 'preact/compat',
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/proxy-api': {
        target: 'http://app:8091',
        changeOrigin: false,
        rewrite: (path) => path.replace(/^\/proxy-api/, ''),
      },
    },
  },
});