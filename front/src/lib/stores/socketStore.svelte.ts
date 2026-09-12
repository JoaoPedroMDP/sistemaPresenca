/**
 *  Último erro devolvido pelo back no WebSocket (evento "error").
 *  O painel mostra a mensagem e volta para o input do nome do evento.
 */
const store = $state({
    error: null as string | null,
    setError(message: string) {
        store.error = message;
    },
    clearError() {
        store.error = null;
    }
})

export default store;
