import ApiResponse from "./index.svelte";
import { callFetch } from "./index.svelte";

/**
 *  Rotas do modo dispositivo. O código do aparelho é a credencial e vai no
 *  path; sem ele válido e ativado o back responde 401.
 */

async function errorMessage(response: Response): Promise<string> {
    try {
        return (await response.json()).error ?? response.statusText;
    } catch {
        return response.statusText;
    }
}

/** Uso único: resgata o código escaneado e prende este aparelho a ele. */
async function callActivateDevice(code: string): Promise<ApiResponse> {
    let response = await callFetch({
        input: `/api/checkin/device/${code}/activate`,
        init: { method: "POST" },
        ensureLogin: false,
    });

    if (!response.ok) {
        return new ApiResponse(false, await errorMessage(response), { status: response.status });
    }
    return new ApiResponse(true, "Dispositivo ativado", await response.json());
}

async function callDevicePendingMembers(code: string): Promise<ApiResponse> {
    let response = await callFetch({
        input: `/api/checkin/device/${code}/pending`,
        ensureLogin: false,
    });

    if (!response.ok) {
        return new ApiResponse(false, await errorMessage(response), { status: response.status });
    }
    return new ApiResponse(true, "Membros pendentes", await response.json());
}

async function callDeviceCheckin(code: string, memberId: number): Promise<ApiResponse> {
    let response = await callFetch({
        input: `/api/checkin/device/${code}/${memberId}`,
        init: { method: "POST" },
        ensureLogin: false,
    });

    if (!response.ok) {
        return new ApiResponse(false, await errorMessage(response), { status: response.status });
    }
    return new ApiResponse(true, "Presença marcada", await response.json());
}

export { callActivateDevice, callDevicePendingMembers, callDeviceCheckin };
