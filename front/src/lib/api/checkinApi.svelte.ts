import ApiResponse from "./index.svelte";
import { callFetch } from "./index.svelte";
import type { MemberCheckin } from "$lib/stores/checkinStore.svelte";
import type { PendingMember } from "$lib/types/api";

// Datas ISO dos check-ins agrupadas por nome do evento
type CheckinHistory = Record<string, string[]>;

async function callGetHistory(): Promise<ApiResponse<CheckinHistory>> {
    let response = await callFetch({ input: 'api/checkin/history' });

    if (!response.ok) {
        console.log("Erro ao buscar histórico:", response.status, response.statusText);
        return new ApiResponse(false, response.statusText);
    }
    return new ApiResponse(true, "Histórico de checkins", await response.json());
}

async function callAlreadyCheckedIn(eventName: string): Promise<ApiResponse<{ members: MemberCheckin[] }>> {
    let response = await callFetch({input: `api/checkin/already/${eventName}`, ensureLogin: false });

    if (!response.ok) {
        console.log("Erro ao verificar checkin:", response.status, response.statusText);
        return new ApiResponse(false, response.statusText);
    }
    return new ApiResponse(true, "Verificação de checkin", await response.json());
}

async function callPendingMembers(code: string): Promise<ApiResponse<{ members: PendingMember[] }>> {
    let response = await callFetch({ input: `/api/checkin/pending/${code}`});
    if (!response.ok) {
        console.log("Erro ao buscar membros pendentes:", response.status, response.statusText);
        return new ApiResponse(false, (await response.json()).error ?? response.statusText);
    }
    return new ApiResponse(true, "Membros pendentes", await response.json());
}

export { callGetHistory, callAlreadyCheckedIn, callPendingMembers };
export type { CheckinHistory };
