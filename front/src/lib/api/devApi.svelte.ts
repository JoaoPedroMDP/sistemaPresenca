import ApiResponse from "./index.svelte";
import { callFetch } from "./index.svelte";

/**
 *  Rotas do simulador de check-in. O back só monta /api/dev/ com DEBUG ligado,
 *  então em produção tudo aqui responde 404.
 */

interface DevMember {
    id: number;
    name: string;
    photo: string | null;
    birthday: string | null;
    checked_in_today: boolean;
}

interface DevMembers {
    event: string;
    members: DevMember[];
}

interface DevCheckinResult {
    id: number;
    name: string | null;
    points: number | null;
    /** Já tinha check-in hoje: o painel não foi notificado de novo */
    already: boolean;
    error?: string;
}

interface DevResetCounts {
    checkins: number;
    scores: number;
    scoreboards: number;
}

async function errorMessage(response: Response): Promise<string> {
    try {
        return (await response.json()).error ?? response.statusText;
    } catch {
        return response.statusText;
    }
}

async function failure<T>(response: Response): Promise<ApiResponse<T>> {
    return new ApiResponse<T>(false, await errorMessage(response), undefined, response.status);
}

async function callDevEvents(): Promise<ApiResponse<{ events: string[] }>> {
    let response = await callFetch({ input: "/api/dev/events", ensureLogin: false });

    if (!response.ok) {
        return await failure(response);
    }
    return new ApiResponse(true, "Eventos", await response.json());
}

async function callDevMembers(eventName: string): Promise<ApiResponse<DevMembers>> {
    let response = await callFetch({
        input: `/api/dev/members/${encodeURIComponent(eventName)}`,
        ensureLogin: false,
    });

    if (!response.ok) {
        return await failure(response);
    }
    return new ApiResponse(true, "Membros", await response.json());
}

async function callDevCheckin(
    eventName: string, memberIds: number[]
): Promise<ApiResponse<{ results: DevCheckinResult[] }>> {
    let response = await callFetch({
        input: "/api/dev/checkin",
        init: {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ event: eventName, member_ids: memberIds }),
        },
        ensureLogin: false,
    });

    if (!response.ok) {
        return await failure(response);
    }
    return new ApiResponse(true, "Check-ins simulados", await response.json());
}

async function callDevReset(): Promise<ApiResponse<{ deleted: DevResetCounts }>> {
    let response = await callFetch({
        input: "/api/dev/reset",
        init: { method: "POST" },
        ensureLogin: false,
    });

    if (!response.ok) {
        return await failure(response);
    }
    return new ApiResponse(true, "Reset feito", await response.json());
}

export { callDevEvents, callDevMembers, callDevCheckin, callDevReset };
export type { DevMember, DevMembers, DevCheckinResult, DevResetCounts };
