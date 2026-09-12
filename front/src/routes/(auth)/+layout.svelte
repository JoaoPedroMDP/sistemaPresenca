<script lang="ts">
    import type { Snippet } from "svelte";
    import authStore from "$lib/stores/authStore.svelte";
    
    let checkedAuth = $state(false);
    interface Props {
		children?: Snippet;
	}

	const props: Props = $props();

    // Só renderiza a página depois da resposta do back; sem sessão vai
    // direto para o login
    $effect(() => {
        authStore.getLoggedFromServer().then(async (logged) => {
            if(!logged){
                await authStore.goToLogin();
                return;
            }
            checkedAuth = true;
        });
    })

    async function logout(){
        await authStore.logout();
        await authStore.goToLogin();
    }
</script>

<div class="min-h-full flex flex-col">
    {#if checkedAuth}
        <nav class="flex items-center justify-between p-4 bg-indigo-900 text-white">
            <span class="text-xl font-bold">Jovens AV</span>
            <div class="flex gap-4">
                <a href="/me" class="hover:underline">Perfil</a>
                <button onclick={logout} class="hover:underline">Sair</button>
            </div>
        </nav>
        {@render props.children?.()}

    {:else}
        <div class="flex-1 flex items-center justify-center">
            <span class="text-2xl text-indigo-900">Verificando autenticação...</span>
        </div>
    {/if}
</div>