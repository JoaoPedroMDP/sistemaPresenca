import ApiResponse, { getCsrfToken } from "./index.svelte";
import { callFetch } from "./index.svelte";


async function callMe(): Promise<ApiResponse> {
    let response = await callFetch({ input: 'api/member/me' });

    if (!response.ok) {
        console.log("Erro ao buscar membro:", response.status, response.statusText);
        return new ApiResponse(false, response.statusText);
    }
    return new ApiResponse(true, "Sucesso", await response.json());
}

/**
 * Envia uma nova foto de perfil para o back-end.
 * @param photo Blob JPEG/PNG já recortado e pronto para upload.
 */
async function callSetPhoto(photo: Blob): Promise<ApiResponse> {
    const formData = new FormData();
    formData.append('photo', photo, 'profile.jpg');
    formData.append('csrfmiddlewaretoken', getCsrfToken());
    const response = await callFetch({
        input: 'api/member/photo',
        init: {
            method: 'POST',
            body: formData,
            // Note: Do not set Content-Type header; the browser will add the correct boundary for multipart/form-data
            // Não defina Content-Type manualmente; o browser injeta o boundary correto
        }
    });

    if (!response.ok) {
        console.log("Erro ao enviar foto:", response.status, response.statusText);
        return new ApiResponse(false, response.statusText);
    }
    return new ApiResponse(true, "Foto atualizada com sucesso", await response.json().catch(() => null));
}

export { callMe, callSetPhoto };