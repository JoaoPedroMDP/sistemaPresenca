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
            console.warn(`WebSocket fechou (code: ${event.code}). Reconectando em 3s...`);
            socket.current = null;
            if(event.code !== 1000){
                console.error('WebSocket fechado inesperadamente:', event);

            }else{
                console.log('WebSocket fechado normalmente.');
                setTimeout(() => createSocket(event_name), 3000);
            }
        };
    });

}

export function initSocket(event_name: string): Promise<boolean> {
    if (socket.current) return Promise.resolve(true);

    return createSocket(event_name);
}

export default socket;