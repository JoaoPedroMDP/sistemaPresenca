import authStore from "$lib/stores/authStore.svelte";

class ApiResponse {
    success: boolean;
    message: string;
    data?: object;

    constructor(success: boolean, message: string, data?: object) {
        this.success = success;
        this.message = message;
        if (data) {
            this.data = data;
        }
    }
}
interface Params {
    input: RequestInfo;
    init?: RequestInit;
    ensureLogin?: boolean;
}
async function callFetch({ input, init, ensureLogin = true }: Params): Promise<Response> {
    try {
        let response = await fetch(input, init);

        if (!response.ok && response.status == 401 && ensureLogin) {
            authStore.triggerLogin();
        }

        return response;
    } catch (error) {
        console.error("Erro na requisição da API:", error);
        return new Response(null, { status: 500, statusText: "Erro na requisição da API" });
    }

}

export default ApiResponse;
export { callFetch };