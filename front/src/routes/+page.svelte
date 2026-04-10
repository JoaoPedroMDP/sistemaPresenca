<script lang="ts">
	import { onMount } from 'svelte';
	import { initSocket } from '$lib/websocket/socket';
	import QrCode from "$lib/QrCode.svelte";
	import codeStore from "$lib/stores/codeStore.svelte";
	import checkInStore from "$lib/stores/checkinStore.svelte";
	import "$lib/websocket/socket";

	onMount(() => {
		initSocket();
	});
</script>

<div class="flex flex-row items-center justify-center h-dvh gap-8">
	<!-- <span class="text-black">{codeStore.code}</span> -->
	{#if codeStore.code}
		<div class="flex justify-center items-center border-r-2 ">
			<QrCode />
		</div>
	{/if}
		
	<!-- <div class="w-0.5 h-[30%] bg-emerald-400"></div> -->
	<div>
		{#each checkInStore.members as member}
			<p class="text-lg text-indigo-900 mt-2">{member} fez check-in!</p>
		{/each}
	</div>
</div>