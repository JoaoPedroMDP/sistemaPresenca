<script lang="ts">
    import { qr } from '@svelte-put/qr/svg';
    import codeStore from '$lib/stores/codeStore.svelte';
    import logo from '$lib/assets/jovensLogoVerde.png';

    const presenceUrl = $derived(
        codeStore.code
            ? `${window.location.protocol}//${window.location.host}/checkin/${codeStore.code}`
            : null
    )
</script>

<div class="flex flex-col items-center overflow-hidden">
    {#if !presenceUrl}
        <p>Aguardando código...</p>
    {:else}
        <svg
            class="backdrop-blur-xl rounded-2xl"
            use:qr={{
                data: presenceUrl,
                logo: logo,
                shape: 'circle',
                moduleFill: '#312e81',
                anchorOuterFill: '#34d399',
                anchorInnerFill: '#312e81',}}
            width="300"
            height="300"
        />
        {#if import.meta.env.MODE == 'development'}
            <h1 class="text-blue-300">{presenceUrl}</h1>
        {/if}
    {/if}
</div>