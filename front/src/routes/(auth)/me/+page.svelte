<script lang="ts">
    import type { Member } from "$lib/types/api";
    import { onMount } from "svelte";
    import authStore from "$lib/stores/authStore.svelte";
    let member: Member|null = $state(null);
    let checkinHistory: { date: string }[] = $state([]);

    let message = $state('');

    onMount(async () => {
        console.log(authStore.logged)
        member = await authStore.getMember();
    });

    async function getHistory(){
        let response = await fetch('api/checkin/history');
        if(!response.ok){
            message = response.statusText;
            return;
        }

        let data = await response.json();
        checkinHistory = data;
    }

    $effect(() => {
        if(member){
            document.title = `Perfil - ${member.name}`;
            getHistory();
        } else {
            document.title = 'Buscando...';
        }
    });
</script>

<div class="flex flex-col h-dvh justify-center items-center px-100">
    <span class="text-black text-2xl">{message}</span>
    {#if member}
        <div class="flex flex-col gap-4 rounded-xl p-4  ring-1 ring-indigo-900 shadow-xl w-full">
            <div class="flex">
                <h1 class="text-black text-2xl">{member.name}</h1>
            </div>
            <div class="flex items-center text-black text-2xl gap-4">
                <span class="icon-[fa6-solid--cake-candles]"></span>
                <span class="leading-none">{new Date(member.birthday ?? new Date()).toLocaleDateString()}</span>
            </div>
            <span class="text-gray-500 text-sm">{member.user?.username}</span>
        </div>
        {#if checkinHistory.length > 0}
            <div class="flex flex-col items-center p-4 ring-1 ring-indigo-900 rounded-xl w-full gap-2 mt-4">
                <span class="text-black self-start text-xl">Histórico de Presença:</span>
                {#each checkinHistory as checkin}
                    <span class="text-black">{
                        new Date(checkin.date).toLocaleString(
                            "pt-BR", 
                            { dateStyle: 'short', timeStyle: 'short' }
                        )
                    }</span>
                {/each}
            </div>
        {:else}
            <span class="text-gray-500 mt-4">Nenhuma presença registrada.</span>
        {/if}
    {/if}
</div>