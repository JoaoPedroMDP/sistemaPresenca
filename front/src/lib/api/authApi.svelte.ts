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

    // Erro vem com status HTTP real (400/401) e a mensagem no corpo
    if(!response.ok){
        let message = response.statusText;
        try {
            message = (await response.json()).error ?? message;
        } catch {}
        console.log("Erro no login:", response.status, message);
        return new ApiResponse(false, message);
    }

    return new ApiResponse(true, "Login successful", await response.json());
}


async function callLogged(): Promise<ApiResponse> {
    let response = await callFetch({
        input: "/api/auth/logged",
        ensureLogin: false,
    });

    if(!response.ok){
        console.log("Usuário não está logado:", response.status, response.statusText);
        return new ApiResponse(false, response.statusText);
    }
    return new ApiResponse(true, "Usuário está logado", await response.json());

}
export { callLogout, callLogin, callLogged };