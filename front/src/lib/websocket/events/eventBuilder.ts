import type { RawPayload } from "$events/types";
import type SocketEvent from "$events";
import { SocketEventList } from "$events/types";
import MemberCheckinEvent from "./memberCheckinEvent";
import NewCodeEvent from "./newCodeEvent";

export default function build(raw_payload: string): SocketEvent {
    const payload: RawPayload = JSON.parse(raw_payload);
    switch (payload.type) {
        case SocketEventList.CHECKIN:
            return new MemberCheckinEvent(raw_payload);
        case SocketEventList.NEW_CODE:
            return new NewCodeEvent(raw_payload);
        default:
            throw new Error(`Unknown event type: ${payload.type}`);
    }
}