// import { defineConfig } from 'vite'
// import react from '@vitejs/plugin-react'

// export default defineConfig({
//   plugins: [react()],
//   build: {
//     outDir: 'dist',
//     sourcemap: false,
//     rollupOptions: {
//       output: {
//         manualChunks: undefined,
//       },
//     },
//   },
//   server: {
//     proxy: {
//       '/api': {
//         target: 'http://localhost:8080',
//         changeOrigin: true,
//       },
//     },
//   },
// })
// import { defineConfig } from 'vite';
// import react from '@vitejs/plugin-react';

// // Set base to your repo name for GitHub Pages
// export default defineConfig({
//   base: '/privacyTrustByDesignHackerearth/',
//   plugins: [react()],
// });
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  base: '/privacyTrustByDesignHackerearth/', // GitHub repo name
  plugins: [react()],
});

