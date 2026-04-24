<script lang="ts">
	import { initSocket } from '$lib/websocket/socket';
	import QrCode from "$lib/components/QrCode.svelte";
	import codeStore from "$lib/stores/codeStore.svelte";
	import "$lib/websocket/socket";
    import Text from '$lib/inputs/Text.svelte';
    import Phloating from '$lib/components/Phloating.svelte';
    import type { PhloatingHandlers } from '$lib/components/Phloating.svelte';
	import checkinStore, { type MemberCheckin } from '$lib/stores/checkinStore.svelte';

	let connected: boolean = $state(false);
	let event_name: string = $state('Escola Sabatina');

	let phloating: PhloatingHandlers | null = $state(null); 

	async function enterGroup(group_name: string) : Promise<void> {
		connected = await initSocket(group_name);
		console.log(connected);
	}

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
		phloating.addPhoto({id: member.name, name: member.name, src: member.photo});
	}

	checkinStore.registerObserver(memberCheckin);
</script>

<div class="flex flex-row items-center justify-center h-dvh gap-8 text-black">
	{#if !connected}
		<div class="flex flex-col items-center gap-4">
			<p class="text-2xl text-indigo-900">Digite o nome do evento para gerar o QR Code</p>
			<Text bind:value={event_name} {onkeyup}/>
		</div>
	{:else}
		{#if codeStore.code}
			<div class="absolute flex justify-center items-center w-min z-10">
				<QrCode />
			</div>
		{/if}

		<div>
			<Phloating bind:this={phloating}/>
		</div>
	{/if}
</div>