<script lang="ts">
	import { closeSocket, initSocket } from '$lib/websocket/socket';
	import socketStore from '$lib/stores/socketStore.svelte';
	import QrCode from "$lib/components/QrCode.svelte";
	import codeStore from "$lib/stores/codeStore.svelte";
	import "$lib/websocket/socket";
    import Text from '$lib/inputs/Text.svelte';
    import Phloating from '$lib/components/Phloating.svelte';
    import type { ScoreEntry } from '$lib/types/api';
	import checkinStore, { type MemberCheckin } from '$lib/stores/checkinStore.svelte';
    import { callAlreadyCheckedIn } from '$lib/api/checkinApi.svelte';
    import Button from '$lib/inputs/Button.svelte';
    import { callGetEventScoreboard } from '$lib/api/scoreApi.svelte';
    import { isBirthWeek } from '$lib/dateUtils';

	let connected: boolean = $state(false);
	let event_name: string = $state('Escola Sabatina');
	let scoreboard = $state<ScoreEntry[]>([]);
	let phloating: ReturnType<typeof Phloating> | null = $state(null);

	async function loadPreviousCheckins(group_name: string){
		let response = await callAlreadyCheckedIn(group_name);
		if(response.success && response.data){
			response.data.members.forEach(member => {
				memberCheckin(member);
			});
		}
		else{
			console.error("Failed to fetch already checked-in members:", response.message);
		}
	}

	async function loadScoreboard(scoreboard_name: string){
		let response = await callGetEventScoreboard(scoreboard_name);
		if(response.success && response.data){
			scoreboard = response.data.data;
		}
	}

	async function enterGroup(group_name: string) : Promise<void> {
		socketStore.clearError();
		connected = await initSocket(group_name);
		if(connected){
			await loadPreviousCheckins(group_name);
			await loadScoreboard(group_name);
			console.log("Connected to group:", group_name);
		}
	}

	// O back recusou o joinEvent (nome errado, por exemplo): fecha o socket
	// e volta para o input, com a mensagem embaixo dele
	$effect(() => {
		if(socketStore.error && connected){
			closeSocket();
			connected = false;
		}
	});

	async function onkeyup(e: KeyboardEvent): Promise<void> {
		if(e.key === 'Enter'){
			await enterGroup(event_name);
		}
	}

	function memberCheckin(member: MemberCheckin) {
		if(!phloating){
			console.log("Phloating component not initialized yet");
			return;
		}

		let extras = {
			birthday: isBirthWeek(member.birthday)
		};

		phloating.addPhoto(
			{id: member.name, name: member.name, src: member.photo},
			extras
		);
	}

	checkinStore.registerObserver(memberCheckin);
</script>

<div class="flex flex-row items-center justify-center h-dvh gap-8 text-black">
	{#if !connected}
		<div class="flex flex-col items-center gap-4">
			<p class="text-2xl text-center text-indigo-900">Digite o nome do evento para gerar o QR Code</p>
			<Text bind:value={event_name} {onkeyup}/>
			{#if socketStore.error}
				<span class="text-red-500 text-sm text-center">{socketStore.error}</span>
			{/if}
			<Button onclick={() => enterGroup(event_name)} text="Entrar"></Button>
		</div>
	{:else}
		{#if codeStore.code}
		<div class="flex flex-col items-center gap-4">
			<h1 class="text-4xl text-center text-indigo-900 z-10">Registre sua presença!!</h1>
			<div class="relative flex justify-center items-center w-min z-10">
				<QrCode />
			</div>
			<Phloating bind:this={phloating}/>
		</div>
		{/if}
		{#if scoreboard && scoreboard.length > 0}
		<div class="flex flex-col gap-2 min-w-[220px] backdrop-blur-md rounded-2xl p-4 z-10">
			<p class="text-sm text-center text-indigo-400 tracking-wide">Placar</p>
			{#each scoreboard.slice(0, 4) as entry, i}
			<div class={`flex items-center gap-3 px-4 py-2.5 rounded-xl ${i === 0 ? 'bg-emerald-500' : ''}`}>
				<span class="text-xs font-medium {i === 0 ? 'text-indigo-700' : 'text-gray-400'} w-5">{i + 1}º</span>
				<span class="flex-1 text-sm {i === 0 ? 'font-semibold text-indigo-900' : 'text-gray-700'}">{entry.name}</span>
				{#if entry.score > 0}
					<span class="text-sm font-medium {i === 0 ? 'text-indigo-900' : 'text-gray-700'}">{entry.score}</span>				
				{/if}
			</div>
			{/each}
		</div>
		{/if}
	{/if}
</div>