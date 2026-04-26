import ApiResponse, { callFetch } from "./index.svelte";

async function callLogout(): Promise<ApiResponse> {
    let response = await callFetch({
        input: "/api/auth/logout",
        ensureLogin: false
    });
    return new ApiResponse(response.ok, response.statusText);
}


async function callLogin(username: string, password: string): Promise<ApiResponse> {
    let response = await callFetch({
        input: "/api/auth/login",
        init: {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        },
        ensureLogin: false,
    });

    if(!response.ok){
        console.log("Erro no login:", response.status, response.statusText);
        return new ApiResponse(false, response.statusText);
    }

    let data = await response.json();
    if(data.error){
        console.log("Erro na resposta do login:", data.error);
        return new ApiResponse(false, data.error);
    }
    return new ApiResponse(true, "Login successful", data);
}


async function callLogged(): Promise<ApiResponse> {
    let response = await callFetch({
        input: "/api/auth/logged"
    });

    if(!response.ok){
        console.log("Usuário não está logado:", response.status, response.statusText);
        return new ApiResponse(false, response.statusText);
    }
    return new ApiResponse(true, "Usuário está logado", await response.json());

}
export { callLogout, callLogin, callLogged };