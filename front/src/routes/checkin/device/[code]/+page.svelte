<script lang="ts">
    import { onMount } from "svelte";

    import Member from "$lib/components/Member.svelte";
    import Button from "$lib/inputs/Button.svelte";
    import { isBirthWeek } from "$lib/dateUtils";
    import { LSLoadDevice, LSSaveDevice } from "$lib/storage/deviceStorage";
    import {
        callActivateDevice,
        callDeviceCheckin,
        callDevicePendingMembers,
        type DevicePendingMember as PendingMember,
    } from "$lib/api/deviceApi.svelte";
    import type { PageProps } from "./$types";

    const PHOTO_SIZE = 84;
    const BACK_TO_LIST_SECONDS = 3;

    let { params }: PageProps = $props();

    let activating = $state(true);
    let activationError: string | null = $state(null);
    // Aparelho já ativado que perdeu o acesso (revogado ou expirado no admin)
    let accessError: string | null = $state(null);
    let eventName = $state("");

    let members: PendingMember[] = $state([]);
    let search = $state("");
    let doneToday = $state(0);

    let selected: PendingMember | null = $state(null);
    let success: boolean | null = $state(null);
    let pointsEarned: number | null = $state(null);
    let secondsLeft = $state(BACK_TO_LIST_SECONDS);
    let checkinError: string | null = $state(null);

    let filtered = $derived(
        members.filter(m => m.name.toLowerCase().includes(search.trim().toLowerCase()))
    );

    /**
     *  Primeira visita neste aparelho: o código vem do QR mostrado no admin e
     *  precisa ser resgatado. Uso único — só o primeiro aparelho é liberado.
     *  Depois disso o código fica guardado e a lista abre direto.
     */
    async function activate() {
        const stored = LSLoadDevice();
        if (stored?.code === params.code) {
            eventName = stored.event;
            activating = false;
            return;
        }

        const response = await callActivateDevice(params.code);
        if (!response.success || !response.data) {
            activationError = response.message;
            activating = false;
            return;
        }

        eventName = response.data.event;
        LSSaveDevice({ code: params.code, event: response.data.event }, response.data.expiresAt);
        activating = false;
    }

    async function loadPending() {
        const response = await callDevicePendingMembers(params.code);
        if (!response.success || !response.data) {
            accessError = response.message;
            return;
        }

        eventName = response.data.event;
        members = response.data.members;
    }

    function pick(member: PendingMember) {
        selected = member;
        success = null;
        checkinError = null;
    }

    function backToList() {
        selected = null;
        success = null;
        pointsEarned = null;
        search = "";
    }

    async function confirmCheckin() {
        if (!selected) return;

        const response = await callDeviceCheckin(params.code, selected.id);
        if (!response.success) {
            checkinError = response.message;
            return;
        }

        pointsEarned = response.data?.points ?? null;
        success = true;
        doneToday += 1;
        members = members.filter(m => m.id !== selected?.id);

        // Volta sozinho: o aparelho já está na mão da próxima pessoa
        secondsLeft = BACK_TO_LIST_SECONDS;
        const timer = setInterval(() => {
            secondsLeft -= 1;
            if (secondsLeft <= 0) {
                clearInterval(timer);
                backToList();
            }
        }, 1000);
    }

    onMount(async () => {
        await activate();
        if (!activationError) {
            await loadPending();
        }
    });
</script>

{#if activating || activationError || accessError}
    <div class="flex flex-col items-center justify-center gap-5 h-dvh p-6 text-center bg-white">
        {#if activationError}
            <p class="text-xl font-semibold text-red-600">Não foi possível ativar este dispositivo</p>
            <p class="text-indigo-900">{activationError}</p>
            <p class="text-gray-500 max-w-lg">Peça um novo código no admin e escaneie o QR Code de novo.</p>
        {:else if accessError}
            <p class="text-xl font-semibold text-red-600">Este dispositivo perdeu o acesso</p>
            <p class="text-indigo-900">{accessError}</p>
            <p class="text-gray-500 max-w-lg">O acesso foi revogado ou expirou. Peça um novo código no admin e escaneie o QR Code de novo.</p>
        {:else}
            <div class="spinner"></div>
            <h1 class="text-2xl text-indigo-900">Ativando este dispositivo…</h1>
            <p class="text-gray-500 max-w-lg">
                Depois disso o aparelho pode passar de mão em mão: cada pessoa acha o
                próprio nome e registra a presença, sem escanear nada.
            </p>
        {/if}
    </div>
{:else if selected}
    <div id="main" data-success={success}
        class="relative flex flex-col items-center justify-center gap-5 h-dvh p-6 overflow-hidden bg-white">
        <div id="content" data-success={success} class="z-10 flex flex-col items-center gap-5">
            <Member
                name={selected.name}
                photo={selected.photo}
                birthday={isBirthWeek(selected.birthday)}
                size={190}
                showName={false}
            />
            <h1 class="text-3xl text-center text-indigo-900">{selected.name}</h1>
            <p class="text-gray-500">Confirme que é você para registrar a presença</p>
            {#if checkinError}
                <p class="text-red-600">{checkinError}</p>
            {/if}
            <div class="flex flex-row gap-3">
                <Button onclick={backToList} text="Não sou eu" cls="bg-transparent border-2 text-indigo-900" />
                <Button onclick={confirmCheckin} text="Sou eu" cls="bg-emerald-600" />
            </div>
        </div>

        {#if pointsEarned && pointsEarned > 0}
            <span id="points" data-success={success} class="text-black text-2xl z-10">+ {pointsEarned}pts</span>
        {/if}

        <div id="done-msg" data-success={success} class="z-20 flex flex-col items-center gap-2 text-white text-center">
            <span class="text-4xl">Presença registrada!</span>
            <span class="text-base opacity-85">Passe o tablet para a próxima pessoa</span>
            <span class="text-base opacity-85">Voltando à lista em {secondsLeft}s</span>
        </div>
    </div>
{:else}
    <div class="flex flex-col h-dvh bg-white">
        <header class="flex items-center gap-4 px-6 py-4 bg-indigo-900 text-white">
            <div class="flex flex-col gap-0.5">
                <strong class="text-xl font-semibold">{eventName}</strong>
                <span class="text-xs opacity-75">
                    {new Date().toLocaleDateString('pt-BR', { dateStyle: 'full' })}
                </span>
            </div>
        </header>

        <div class="flex items-center gap-3 px-6 pt-4 pb-1">
            <input
                class="flex-1 text-lg p-2 text-indigo-900 border-3 rounded-lg border-emerald-500 outline-none"
                placeholder="Buscar seu nome…"
                autocomplete="off"
                bind:value={search}
            />
            <span class="px-3 py-1 rounded-full bg-gray-100 text-gray-700 text-sm">
                {members.length} pendentes
            </span>
        </div>

        <div class="grid gap-4 px-6 pt-4 pb-24 flex-1 min-h-0 overflow-y-auto content-start member-grid">
            {#each filtered as m (m.id)}
                <button
                    class="flex items-center justify-center overflow-hidden pt-7 px-5 pb-4 border-2 border-gray-200
                           rounded-2xl bg-white cursor-pointer hover:border-indigo-500"
                    onclick={() => pick(m)}
                >
                    <Member
                        name={m.name}
                        photo={m.photo}
                        birthday={isBirthWeek(m.birthday)}
                        size={PHOTO_SIZE}
                    />
                </button>
            {/each}
        </div>

        {#if filtered.length === 0}
            <p class="py-16 text-center text-gray-500">Nenhum nome encontrado.</p>
        {/if}

        <footer class="fixed bottom-0 left-0 right-0 flex items-center justify-between px-6 py-3
                       bg-white border-t border-gray-200 text-sm text-gray-500">
            <span>Toque no seu nome para registrar presença</span>
            <span class="px-3 py-1 rounded-full bg-emerald-500 text-white">{doneToday} presentes hoje</span>
        </footer>
    </div>
{/if}

<style>
    .member-grid {
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    }

    .spinner {
        width: 2.5rem;
        height: 2.5rem;
        border-radius: 50%;
        border: 4px solid var(--color-gray-200);
        border-top-color: var(--color-indigo-700);
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    /* Mesma onda verde do check-in por QR */
    #content {
        transform: scale(1);
        transition: transform 0.7s cubic-bezier(.49,-0.43,.65,.83);
    }

    #content[data-success="true"] {
        transform: scale(0);
    }

    #main:before {
        z-index: 0;
        content: '';
        width: 10px;
        height: 10px;
        border-radius: 50%;
        position: absolute;
        background-color: transparent;
        transform: scale(1);
        transition: transform 1.5s ease-in-out;
        overflow: hidden;
    }

    #main[data-success="true"]:before {
        background-color: var(--color-emerald-500);
        transform: scale(300);
    }

    #points {
        position: absolute;
        bottom: -5%;
        transform: scale(1);
        transition:
            bottom 1.5s cubic-bezier(.29,.85,.66,.99),
            transform 1.6s cubic-bezier(.5,.52,.69,.61);
    }

    #points[data-success="true"] {
        transform: scale(2);
        bottom: 50%;
    }

    #done-msg {
        position: absolute;
        opacity: 0;
        transition: opacity 0.5s ease 1.4s;
    }

    #done-msg[data-success="true"] {
        opacity: 1;
    }
</style>
