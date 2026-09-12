import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';
import { readFileSync } from 'node:fs';

function czVersion(): string {
    try {
        const cz = JSON.parse(readFileSync(new URL('../cz.json', import.meta.url), 'utf-8'));
        return cz.commitizen.version;
    } catch {
        return 'dev';
    }
}

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd(), 'VITE_');
    const allowedHosts = env.VITE_ALLOWED_HOSTS?.split(',').map((h) => h.trim()).filter(Boolean);

    return {
        plugins: [tailwindcss(), sveltekit()],
        define: {
            __APP_VERSION__: JSON.stringify(czVersion())
        },
        server: {
            ...(mode === 'development' && allowedHosts ? { allowedHosts } : {}),
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
    };
});
