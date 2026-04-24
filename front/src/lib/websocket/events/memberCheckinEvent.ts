import SocketEvent from "$events";
import checkinStore from '$lib/stores/checkinStore.svelte';

import type { CheckinPayload } from "./types";

class MemberCheckinEvent extends SocketEvent {
    name: string;
    photo: string | null;

    constructor(raw_payload: string) {
        super(raw_payload);
        const p = this.payload as CheckinPayload;
        this.name = p.member.name;
        this.photo = p.member.photo;
    }

    handle(): void {
        checkinStore.addMember(this.name, this.photo);
    }
}

export default MemberCheckinEvent;