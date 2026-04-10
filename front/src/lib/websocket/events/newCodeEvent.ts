import SocketEvent from "$events";
import type { NewCodePayload } from "./types";
import codeStore from '$lib/stores/codeStore.svelte';

class NewCodeEvent extends SocketEvent {
    code: string;

    constructor(raw_payload: string) {
        super(raw_payload);
        const p = this.payload as NewCodePayload;
        this.code = p.code;
    }

    handle(): void {
        codeStore.setCode(this.code);
    }
}

export default NewCodeEvent;