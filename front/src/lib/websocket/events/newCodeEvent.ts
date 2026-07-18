import SocketEvent from "$events";
import type { NewCodePayload } from "./types";
import codeStore from '$lib/stores/codeStore.svelte';

class NewCodeEvent extends SocketEvent {
    code: string;
    expiresAt: string;

    constructor(raw_payload: string) {
        super(raw_payload);
        const p = this.payload as NewCodePayload;
        this.code = p.code;
        this.expiresAt = p.expiresAt;
    }

    handle(): void {
        codeStore.setCode(this.code, this.expiresAt);
    }
}

export default NewCodeEvent;