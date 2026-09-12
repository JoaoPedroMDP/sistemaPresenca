import SocketEvent from "$events";
import socketStore from '$lib/stores/socketStore.svelte';

import type { ErrorPayload } from "./types";

/** O back recusou algo (evento inexistente, falha ao entrar no grupo). */
class ErrorEvent extends SocketEvent {
    message: string;

    constructor(raw_payload: string) {
        super(raw_payload);
        this.message = (this.payload as ErrorPayload).message;
    }

    handle(): void {
        socketStore.setError(this.message);
    }
}

export default ErrorEvent;
