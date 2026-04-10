import { SocketEventList } from "$events/types";
import type { RawPayload } from "./types";

class SocketEvent {
    type: SocketEventList;
    payload: object;

    constructor(raw_payload: string) {
        const payload: RawPayload = JSON.parse(raw_payload);
        this.type = payload.type;
        this.payload = payload;
    }

    handle(): void {
        console.warn('handle() não implementado para o tipo:', this.type);
    }
}

export default SocketEvent;