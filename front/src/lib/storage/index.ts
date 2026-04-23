import { browser } from "$app/environment";

interface StoredDataT {
    version: number;
    expiresAt?: string | null;
    data: any | null;
}

function loadFromLS(key: string, version: number, defaults: StoredDataT) {
    let parsed: StoredDataT = structuredClone(defaults);
    try{
        const raw = localStorage.getItem(key);
        if(raw){
            parsed = JSON.parse(raw);
        }
    }catch(e){
        console.error(`Failed to load ${key} from localStorage`, e);
    }

    if(parsed.version !== version){
        console.warn(`Failed to load ${key} from localStorage`);
        parsed = structuredClone(defaults);
    }

    if(parsed.expiresAt && new Date(parsed.expiresAt) < new Date()){
        console.warn(`${key} expired at ${parsed.expiresAt}`);
        parsed = structuredClone(defaults);
    }

    return parsed;
}

function saveToLS(data: StoredDataT, key: string) {
    data.expiresAt = new Date(new Date().getTime() + 7 * 24 * 60 * 60 * 1000).toISOString(); // Expira em 7 dias
    try{
        localStorage.setItem(key, JSON.stringify(data));
    }catch(e){
        console.error("Failed to save to localStorage", e);
    }
}

export { loadFromLS, saveToLS };
export type { StoredDataT };