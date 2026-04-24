import type { memberI } from "$lib/types/api";
import { loadFromLS, saveToLS, type StoredDataT } from ".";

const KEY = 'member';
const VERSION = 1;

interface MemberT extends StoredDataT {
    data: memberI | null;
}

const DEFAULTS: MemberT = {
    version: VERSION,
    expiresAt: null,
    data: null
};

function LSLoadMember(): memberI | null {
    return loadFromLS(KEY, VERSION, DEFAULTS).data;
}

function LSSaveMember(member: memberI): void {
    let expiresAt = new Date(new Date().getTime() + 5 * 60 * 1000).toISOString(); // Expira em 5 minutos
    let memberData: MemberT = {
        version: VERSION,
        expiresAt: expiresAt,
        data: member
    };
    saveToLS(memberData, KEY);
}

function LSClearMember(): void {
    localStorage.removeItem(KEY);
}

export { LSLoadMember, LSSaveMember, LSClearMember };
export type { MemberT };