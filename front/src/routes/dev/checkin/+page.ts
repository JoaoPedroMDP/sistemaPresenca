import { error } from '@sveltejs/kit';

// A rota existe só no dev server; no build de produção o back nem monta
// /api/dev/, então a tela não teria com o que conversar
export function load() {
    if (!import.meta.env.DEV) {
        error(404, 'Not found');
    }

    return {};
}
