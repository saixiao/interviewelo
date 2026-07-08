import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    // WSL's /mnt/c drvfs mount doesn't propagate inotify events, so native
    // file watching silently misses edits and serves stale HMR output.
    watch: { usePolling: true },
  },
})
