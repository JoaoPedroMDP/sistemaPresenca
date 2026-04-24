import ApiResponse from "./index.svelte";
import { callFetch } from "./index.svelte";


async function callMe(): Promise<ApiResponse> {
    let response = await callFetch({input: 'api/member/me'});
    
    if(!response.ok){
        console.log("Erro no login:", response.status, response.statusText);
        return new ApiResponse(false, response.statusText);
    }
    return new ApiResponse(true, "Sucesso", await response.json());
}

export { callMe };