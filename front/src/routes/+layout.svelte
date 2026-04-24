<script lang="ts">
	import './layout.css';

	import favicon from '$lib/assets/jovensLogoBranca.png';
	import type { Snippet } from 'svelte';
	import '@fontsource-variable/readex-pro/wght.css';
    import { LSClearAuth } from '$lib/storage/authStorage';
    import { LSClearMember } from '$lib/storage/memberStorage';

	interface Props {
		children?: Snippet;
	}

	const props: Props = $props();

	function clearAllStorage(){
		console.log("Limpando localStorage...");
		localStorage.clear();
		location.reload();
	}

	function clearStorage(){
		console.log("Limpando localStorage (menos autenticação)...");
		LSClearMember();
		location.reload();
	}
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>Jovens AV</title>
</svelte:head>

{@render props.children?.()}
{#if import.meta.env.MODE == 'development'}
<div class="absolute top-12 right-0 flex flex-col gap-4">
	<button onclick={clearAllStorage} class="px-4 py-2 bg-indigo-900 text-white rounded-lg mt-4">Recarregar Storage (+auth)</button>
	<button onclick={clearStorage} class="px-4 py-2 bg-indigo-900 text-white rounded-lg mt-4">Recarregar Storage</button>
</div>
{/if}
