import { loadFromLS, saveToLS, type StoredDataT } from ".";

const KEY = 'auth';
const VERSION = 1;

interface Auth {
    loggedAt: string | null;
}

interface AuthT extends StoredDataT {
    data: Auth | null;
}

const DEFAULTS: AuthT = {
    version: VERSION,
    expiresAt: null,
    data: null
}

function LSLoadAuth(): Auth | null {
    return loadFromLS(KEY, VERSION, DEFAULTS).data;
}

function LSSaveAuth(auth: Auth): void {
    let expiresAt = new Date(new Date().getTime() + 5 * 60 * 1000).toISOString(); // Expira em 5 minutos
    let authData: AuthT = {
        version: VERSION,
        expiresAt: expiresAt,
        data: auth
    };
    saveToLS(authData, KEY);
}

function LSClearAuth(): void {
    localStorage.removeItem(KEY);
}

export { LSLoadAuth, LSSaveAuth, LSClearAuth };
export type { AuthT, Auth };