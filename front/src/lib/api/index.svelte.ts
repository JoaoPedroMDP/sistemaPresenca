import authStore from "$lib/stores/authStore.svelte";

/**
 *  Envelope das chamadas à API. T é o corpo esperado em caso de sucesso;
 *  status carrega o HTTP real quando a chamada falha, para o chamador
 *  distinguir 401 de 404, por exemplo.
 */
class ApiResponse<T = object> {
    success: boolean;
    message: string;
    data?: T;
    status?: number;

    constructor(success: boolean, message: string, data?: T, status?: number) {
        this.success = success;
        this.message = message;
        if (data) {
            this.data = data;
        }
        if (status !== undefined) {
            this.status = status;
        }
    }
}
interface Params {
    input: RequestInfo;
    init?: RequestInit;
    ensureLogin?: boolean;
}

function getCsrfToken(): string {
    return document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1] ?? '';
}

async function callFetch({ input, init, ensureLogin = true }: Params): Promise<Response> {
    try {
        let response = await fetch(input, init);

        if (!response.ok && response.status == 401 && ensureLogin) {
            console.log("Usuário não autenticado. Redirecionando para login...");
            await authStore.goToLogin();
        }

        return response;
    } catch (error) {
        console.error("Erro na requisição da API:", error);
        return new Response(null, { status: 500, statusText: "Erro na requisição da API" });
    }

}

export default ApiResponse;
export { callFetch, getCsrfToken };
