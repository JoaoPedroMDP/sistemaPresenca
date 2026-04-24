<script lang="ts">
    import type { Snippet } from "svelte";
    import authStore from "$lib/stores/authStore.svelte";
    import { goto } from "$app/navigation";
    
    let checkedAuth = $state(false);
    interface Props {
		children?: Snippet;
	}

	const props: Props = $props();

    $effect(() => {
        authStore.loginTrigger;
        if(!authStore.isLogged()){
            console.warn("Usuário não autenticado, redirecionando para login");
            goto('/login');
            return;
        }
        checkedAuth = true;
    })
</script>

<div>
    {#if checkedAuth}
        <nav class="flex items-center justify-between p-4 bg-indigo-900 text-white">
            <span class="text-xl font-bold">Jovens AV</span>
            <div class="flex gap-4">
                <a href="/me" class="hover:underline">Perfil</a>
                <button onclick={authStore.logout} class="hover:underline">Sair</button>
            </div>
        </nav>
        {@render props.children?.()}

    {:else}
        <div class="h-dvh flex items-center justify-center">
            <span class="text-2xl text-indigo-900">Verificando autenticação...</span>
        </div>
    {/if}
</div>