<script lang="ts">
	import { onMount } from 'svelte';
	import { initSocket } from '$lib/api/socket';
	import QrCode from "$lib/QrCode.svelte";
	import codeStore from "$lib/codeStore.svelte";
	import "$lib/api/socket";

	onMount(() => {
		initSocket();
	});
</script>

<div class="flex flex-col items-center justify-center h-dvh">
	{#if codeStore.code}
		<div class="flex justify-center items-center">
			<QrCode />
		</div>
	{/if}
</div>