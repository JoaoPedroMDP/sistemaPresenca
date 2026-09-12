import ApiResponse from "./index.svelte";
import { callFetch } from "./index.svelte";

/**
 *  Rotas do modo dispositivo. O código do aparelho é a credencial e vai no
 *  path; sem ele válido e ativado o back responde 401.
 */

interface DevicePendingMember {
    id: number;
    name: string;
    photo: string | null;
    birthday: string | null;
}

interface DeviceActivation {
    event: string;
    expiresAt: string;
}

interface DevicePending {
    event: string;
    members: DevicePendingMember[];
}

interface DeviceCheckin {
    message: string;
    points: number;
}

async function errorMessage(response: Response): Promise<string> {
    try {
        return (await response.json()).error ?? response.statusText;
    } catch {
        return response.statusText;
    }
}

// Resposta de erro sem corpo, guardando o status HTTP para o chamador
async function failure<T>(response: Response): Promise<ApiResponse<T>> {
    return new ApiResponse<T>(false, await errorMessage(response), undefined, response.status);
}

/** Uso único: resgata o código escaneado e prende este aparelho a ele. */
async function callActivateDevice(code: string): Promise<ApiResponse<DeviceActivation>> {
    let response = await callFetch({
        input: `/api/checkin/device/${code}/activate`,
        init: { method: "POST" },
        ensureLogin: false,
    });

    if (!response.ok) {
        return await failure(response);
    }
    return new ApiResponse(true, "Dispositivo ativado", await response.json());
}

async function callDevicePendingMembers(code: string): Promise<ApiResponse<DevicePending>> {
    let response = await callFetch({
        input: `/api/checkin/device/${code}/pending`,
        ensureLogin: false,
    });

    if (!response.ok) {
        return await failure(response);
    }
    return new ApiResponse(true, "Membros pendentes", await response.json());
}

async function callDeviceCheckin(code: string, memberId: number): Promise<ApiResponse<DeviceCheckin>> {
    let response = await callFetch({
        input: `/api/checkin/device/${code}/${memberId}`,
        init: { method: "POST" },
        ensureLogin: false,
    });

    if (!response.ok) {
        return await failure(response);
    }
    return new ApiResponse(true, "Presença marcada", await response.json());
}

export { callActivateDevice, callDevicePendingMembers, callDeviceCheckin };
export type { DevicePendingMember, DeviceActivation, DevicePending, DeviceCheckin };
