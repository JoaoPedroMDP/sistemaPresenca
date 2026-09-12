// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		// interface Locals {}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}

	// Injetada pelo vite.config.ts (define) a partir da versão do cz.json
	const __APP_VERSION__: string;
}

export {};
