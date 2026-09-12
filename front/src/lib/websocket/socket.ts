import type SocketEvent from "./events";
import build from "$events/eventBuilder";


type SocketRef = { current: WebSocket | null };

export const socket: SocketRef = { current: null };

function createSocket(event_name: string): Promise<boolean> {
    // Garante que só roda no browser
    if (typeof window === 'undefined') return Promise.resolve(false);

    return new Promise((resolve) => {
        const WS_URL = `ws://${window.location.host}/ws`;
        const ws = new WebSocket(WS_URL);
    
        ws.onopen = (): void => {
            console.log(`WebSocket conectado em ${WS_URL}`);
            socket.current = ws;
            socket.current.send(JSON.stringify({ type: "joinEvent", event: event_name }));
            console.log(`Solicitado ingresso no evento ${event_name} via WebSocket`);
            resolve(true);
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
            resolve(false);
        };
    
        ws.onclose = (event: CloseEvent): void => {
            socket.current = null;
            // 1000 é fechamento normal (cliente pediu): não reconecta.
            // Qualquer outro código é queda (rede, restart do back): reconecta.
            if(event.code === 1000){
                console.log('WebSocket fechado normalmente.');
                return;
            }

            console.warn(`WebSocket fechou inesperadamente (code: ${event.code}). Reconectando em 3s...`);
            setTimeout(() => createSocket(event_name), 3000);
        };
    });

}

export function initSocket(event_name: string): Promise<boolean> {
    if (socket.current) return Promise.resolve(true);

    return createSocket(event_name);
}

/** Fecha com código 1000 (normal): o onclose não agenda reconexão. */
export function closeSocket(): void {
    socket.current?.close(1000);
    socket.current = null;
}

export default socket;