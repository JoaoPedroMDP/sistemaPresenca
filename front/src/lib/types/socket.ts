import codeStore from '$lib/codeStore.svelte';

enum SocketEventType {
    CHECKIN = 'checkin',
    NEW_CODE = 'newCode'
}

interface RawPayload {
    type: SocketEventType;
    data: string;
}

class SocketEvent {
    type: SocketEventType;
    payload: object;

    constructor(raw_payload: string) {
        const payload: RawPayload = JSON.parse(raw_payload);
        this.type = payload.type;
        this.payload = payload;
    }

    static build(raw_payload: string): SocketEvent {
        const payload: RawPayload = JSON.parse(raw_payload);
        switch (payload.type) {
            case SocketEventType.CHECKIN:
                return new CheckinEvent(raw_payload);
            case SocketEventType.NEW_CODE:
                return new NewCodeEvent(raw_payload);
            default:
                throw new Error(`Unknown event type: ${payload.type}`);
        }
    }

    handle(): void {
        console.warn('handle() não implementado para o tipo:', this.type);
    }
}

class NewCodeEvent extends SocketEvent {
    code: string;

    constructor(raw_payload: string) {
        super(raw_payload);
        this.code = this.payload.code;
    }

    handle(): void {
        codeStore.setCode(this.code);
    }
}

class CheckinEvent extends SocketEvent {
    name: string;

    constructor(raw_payload: string) {
        super(raw_payload);
        this.name = this.data;
    }

    handle(): void {
        console.log('Check-in confirmado para:', this.name);
    }
}

export { SocketEventType, SocketEvent, NewCodeEvent, CheckinEvent };
export type { RawPayload };