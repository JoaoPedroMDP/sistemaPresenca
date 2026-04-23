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
    let expiresAt = new Date(new Date().getTime() + 1 * 24 * 60 * 60 * 1000).toISOString(); // Expira em 1 dia
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