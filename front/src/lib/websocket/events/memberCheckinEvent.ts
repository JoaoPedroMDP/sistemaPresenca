import SocketEvent from "$events";
import checkinStore from '$lib/stores/checkinStore.svelte';

import type { CheckinPayload } from "./types";

class MemberCheckinEvent extends SocketEvent {
    name: string;

    constructor(raw_payload: string) {
        super(raw_payload);
        const p = this.payload as CheckinPayload;
        this.name = p.member;
    }

    handle(): void {
        checkinStore.addMember(this.name);
    }
}

export default MemberCheckinEvent;