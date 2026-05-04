<script lang="ts">
    import type { Member } from "$lib/types/api";
    import { onMount } from "svelte";
    import memberStore from "$lib/stores/memberStore.svelte";
    import PhotoSelector from "$lib/components/PhotoSelector.svelte";
    import { formatDateInUTC } from "$lib/dateUtils";
    import { callGetHistory } from "$lib/api/checkinApi.svelte";
    import { callGetScorePerEvent } from "$lib/api/scoreApi.svelte";

    let member: Member | null = $state(null);
    let checkinHistory: { [key: string]: string[] } = $state({});
    let scorePerEvent: { [key: string]: number } = $state({});
    let message = $state('');

    onMount(async () => {
        member = await memberStore.getMember();
    });

    async function getHistory() {
        let response = await callGetHistory();
        if (!response.success) {
            message = response.message;
            return;
        }

        if(!response.data){
            message = "Nenhum dado retornado.";
            return;
        }

        checkinHistory = response.data;
    }

    async function getScorePerEvent() {
        let response = await callGetScorePerEvent();
        if (!response.success) {
            message = response.message;
            return;
        }

        if(!response.data){
            message = "Nenhum dado retornado.";
            return;
        }

        scorePerEvent = response.data;
    }

    $effect(() => {
        if (member) {
            document.title = `Perfil - ${member.name}`;
            getHistory();
            getScorePerEvent();
        } else {
            document.title = 'Buscando...';
        }
    });
</script>

<div class="flex flex-col justify-center items-center px-10">
    <span class="text-black text-2xl">{message}</span>
    {#if member}
        <div class="flex flex-col gap-4 rounded-xl p-4 items-center  w-full">
            <div class="flex flex-col items-center justify-between w-full gap-2">
                <PhotoSelector
                    bind:src={member.photo}
                    alt={`Foto de perfil de ${member.name}`}
                    onerror={(msg) => (message = msg)}
                />
                <h1 class="text-black text-3xl text-center">{member.name}</h1>
            </div>
            <div class="flex items-center text-black text-2xl gap-4">
                <span class="icon-[fa6-solid--cake-candles]"></span>
                <span class="leading-none">{formatDateInUTC(member.birthday)}</span>
            </div>
            <span class="text-gray-500 text-sm">{member.user?.username}</span>
        </div>
        {#if Object.keys(checkinHistory).length > 0}
            <div class="flex flex-col items-center p-4 ring-1 ring-indigo-900 rounded-xl w-full gap-2 mt-4">
                <span class="text-black self-start text-xl">Histórico de Presença:</span>
                <div class="flex flex-col items-start text-white">
                {#each Object.keys(checkinHistory) as e_name}
                    <div class="flex relative flex-col text-lg bg-emerald-500 self-center rounded-t-2xl p-2 w-full text-black text-center">
                        <h2>{e_name}</h2>
                        <span class="absolute right-0 -top-2 bg-indigo-900 px-1.5 rounded-l-2xl rounded-tr-2xl text-white text-sm">{scorePerEvent[e_name]} pts</span>
                    </div>
                    <div class="flex flex-col px-3 p-2 rounded-b-2xl bg-indigo-900 w-full text-center">
                    {#each checkinHistory[e_name] as c_date}
                        <span class="font-courier">{
                            new Date(c_date).toLocaleString(
                                "pt-BR",
                                { dateStyle: 'short', timeStyle: 'short' }
                            )
                        }</span>
                    {/each}
                    </div>
                {/each}
                </div>
            </div>
        {:else}
            <span class="text-gray-500 mt-4">Nenhuma presença registrada.</span>
        {/if}
    {/if}
</div>