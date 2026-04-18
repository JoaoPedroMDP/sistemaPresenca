<script lang="ts">
	import { initSocket } from '$lib/websocket/socket';
	import QrCode from "$lib/QrCode.svelte";
	import codeStore from "$lib/stores/codeStore.svelte";
	import checkInStore from "$lib/stores/checkinStore.svelte";
	import "$lib/websocket/socket";
    import Text from '$lib/inputs/Text.svelte';

	let connected: boolean = $state(false);
	let event_name: string = $state('Escola Sabatina');

	async function enterGroup(group_name: string) : Promise<void> {
		connected = await initSocket(group_name);
		console.log(connected);
	}

	async function onkeyup(e: KeyboardEvent): Promise<void> {
		if(e.key === 'Enter'){
			await enterGroup(event_name);
		}
	}
</script>

<div class="flex flex-row items-center justify-center h-dvh gap-8 text-black">
	{#if !connected}
		<div class="flex flex-col items-center gap-4">
			<p class="text-2xl text-indigo-900">Digite o nome do evento para gerar o QR Code</p>
			<Text bind:value={event_name} {onkeyup}/>
		</div>
	{:else}
		{#if codeStore.code}
			<div class="flex justify-center items-center">
				<QrCode />
			</div>
		{/if}
			
		<div>
			{#each checkInStore.members as member}
				<p class="text-lg text-indigo-900 mt-2">{member} fez check-in!</p>
			{/each}
		</div>
	{/if}
</div>