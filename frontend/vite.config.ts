import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
	const env = loadEnv(mode, process.cwd(), '');
	const apiBase = env.PUBLIC_API_BASE || 'http://localhost:8000';

	return {
		plugins: [sveltekit()],
		optimizeDeps: {
			exclude: ['layerchart']
		},
		server: {
			proxy: {
				'/api': apiBase,
				'/ws': { target: apiBase, ws: true, changeOrigin: true }
			}
		}
	};
});
