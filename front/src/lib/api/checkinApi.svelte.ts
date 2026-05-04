import ApiResponse from "./index.svelte";
import { callFetch } from "./index.svelte";


async function callGetHistory(): Promise<ApiResponse> {
    let response = await callFetch({ input: 'api/checkin/history' });

    if (!response.ok) {
        console.log("Erro ao buscar histórico:", response.status, response.statusText);
        return new ApiResponse(false, response.statusText);
    }
    return new ApiResponse(true, "Histórico de checkins", await response.json());
}

export { callGetHistory };