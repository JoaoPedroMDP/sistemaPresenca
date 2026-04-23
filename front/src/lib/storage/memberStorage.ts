import type { Member } from "$lib/types/api";
import { loadFromLS, saveToLS, type StoredDataT } from ".";

const KEY = 'member';
const VERSION = 1;

interface MemberT extends StoredDataT {
    data: Member | null;
}

const DEFAULTS: MemberT = {
    version: VERSION,
    expiresAt: null,
    data: null
};

function LSLoadMember(): Member | null {
    return loadFromLS(KEY, VERSION, DEFAULTS).data;
}

function LSSaveMember(member: Member): void {
    let expiresAt = new Date(new Date().getTime() + 1 * 24 * 60 * 60 * 1000).toISOString(); // Expira em 1 dia
    let memberData: MemberT = {
        version: VERSION,
        expiresAt: expiresAt,
        data: member
    };
    saveToLS(memberData, KEY);
}

export { LSLoadMember, LSSaveMember };
export type { MemberT };