<script lang="ts">
    import type { Snippet } from "svelte";
    import authStore from "$lib/stores/authStore.svelte";

    interface Props {
		children?: Snippet;
	}

	const props: Props = $props();

    $effect(() => {
        if(!authStore.logged){
            window.location.href = "/login";
        }
    });
</script>
<div>
    {#if authStore.logged}
        <nav class="flex items-center justify-between p-4 bg-indigo-900 text-white">
            <span class="text-xl font-bold">Jovens AV</span>
            <div class="flex gap-4">
                <a href="/me" class="hover:underline">Perfil</a>
                <button onclick={authStore.logout} class="hover:underline">Sair</button>
            </div>
        </nav>
    {/if}
    {@render props.children?.()}
</div>