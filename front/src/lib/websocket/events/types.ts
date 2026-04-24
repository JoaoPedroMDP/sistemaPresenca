import type { Member } from "$lib/types/api";

export enum SocketEventList {
    CHECKIN = 'memberCheckin',
    NEW_CODE = 'newCode'
}

interface RawPayload {
    type: SocketEventList;
    data: string;
}

interface NewCodePayload extends RawPayload {
    code: string;
}

interface CheckinPayload extends RawPayload {
    member: Member;
}

export type { RawPayload, NewCodePayload, CheckinPayload };