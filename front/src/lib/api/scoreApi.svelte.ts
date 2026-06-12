import ApiResponse from "./index.svelte";
import { callFetch } from "./index.svelte";


async function callGetUserScorePerEvent(): Promise<ApiResponse> {
    let response = await callFetch({input: "api/score/per-event"})
    
    if (!response.ok) {
        console.log("Erro ao buscar score por evento:", response.status, response.statusText);
        return new ApiResponse(false, response.statusText);
    }
    return new ApiResponse(true, "Score por eventos", await response.json());
}


async function callGetEventScoreboard(event_name: string): Promise<ApiResponse> {
    let response = await callFetch({input: `api/score/event/${encodeURIComponent(event_name)}`})

    if (!response.ok) {
        console.log("Erro ao buscar placar do evento:", response.status, response.statusText);
        return new ApiResponse(false, response.statusText);
    }
    return new ApiResponse(true, "Placar do evento", await response.json());
}

export { callGetUserScorePerEvent, callGetEventScoreboard };