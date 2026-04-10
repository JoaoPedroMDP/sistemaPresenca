import type SocketEvent from "./events";
import build from "$events/eventBuilder";


type SocketRef = { current: WebSocket | null };

export const socket: SocketRef = { current: null };

function createSocket(): void {
    // Garante que só roda no browser
    if (typeof window === 'undefined') return;

    const WS_URL = `ws://${window.location.host}/ws`;
    const ws = new WebSocket(WS_URL);

    ws.onopen = (): void => {
        console.log(`WebSocket conectado em ${WS_URL}`);
        socket.current = ws;
    };

    ws.onmessage = (event: MessageEvent<string>): void => {
        try {
            const sevent: SocketEvent = build(event.data);
            sevent.handle();
        } catch (err) {
            console.error('Erro ao processar mensagem WebSocket:', err);
        }
    };

    ws.onerror = (event: Event): void => {
        console.error('WebSocket erro:', event);
    };

    ws.onclose = (event: CloseEvent): void => {
        console.warn(`WebSocket fechou (code: ${event.code}). Reconectando em 3s...`);
        socket.current = null;
        setTimeout(createSocket, 3000);
    };
}

export function initSocket(): void {
    if (socket.current) return; // já conectado
    createSocket();
}

export default socket;