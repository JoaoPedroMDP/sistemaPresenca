import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import { readFileSync } from 'node:fs';

function czVersion(): string {
    try {
        const cz = JSON.parse(readFileSync(new URL('../cz.json', import.meta.url), 'utf-8'));
        return cz.commitizen.version;
    } catch {
        return 'dev';
    }
}

export default defineConfig({
    plugins: [tailwindcss(), sveltekit()],
    define: {
        __APP_VERSION__: JSON.stringify(czVersion())
    },
    server: {
        proxy: {
            '/media': {
                target: 'http://localhost:8000',
                changeOrigin: true,
            },
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true,
            },
            '/ws': {
                target: 'ws://localhost:8000',
                ws: true,
                changeOrigin: true,
            },
        }
    }
});