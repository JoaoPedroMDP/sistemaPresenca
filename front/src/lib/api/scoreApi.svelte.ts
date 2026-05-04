import ApiResponse from "./index.svelte";
import { callFetch } from "./index.svelte";


async function callGetScorePerEvent(): Promise<ApiResponse> {
    let response = await callFetch({input: "api/score/per-event"})
    
    if (!response.ok) {
        console.log("Erro ao buscar score por evento:", response.status, response.statusText);
        return new ApiResponse(false, response.statusText);
    }
    return new ApiResponse(true, "Score por eventos", await response.json());
}

export { callGetScorePerEvent };