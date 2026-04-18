<script lang="ts">
	import './layout.css';

	import favicon from '$lib/assets/jovensLogoBranca.png';
	import type { Snippet } from 'svelte';
	import '@fontsource-variable/readex-pro/wght.css';

	interface Props {
		children?: Snippet;
	}

	const props: Props = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>Jovens AV</title>
</svelte:head>

{@render props.children?.()}
