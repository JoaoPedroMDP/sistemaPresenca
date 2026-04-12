<script lang="ts">
	import { onMount } from 'svelte';
    import codeStore from '$lib/stores/codeStore.svelte';
    import logo from '$lib/assets/jovensLogoVerde.png';

    let error = $state<string | null>(null)

    const presenceUrl = $derived(
        codeStore.code
            ? `${window.location.protocol}//${window.location.host}/checkin/${codeStore.code}`
            : null
    )

    onMount(() => {
        let qrCodeElement = document.getElementById('qrCode');
        if(qrCodeElement){
            qrCodeElement.addEventListener('codeRendered', () => {
                qrCodeElement.animateQRCode('RadialRipple');
            });
        }
    });
</script>

<div class="w-full">
    {#if error}
        <p class="error">Erro ao gerar QR Code: {error}</p>
    {:else if !presenceUrl}
        <p class="waiting">Aguardando código...</p>
    {:else}
        <qr-code
            id="qrCode"
            contents={presenceUrl}
            module-color="var(--color-indigo-900)"
            position-ring-color="var(--color-emerald-400)"
            position-center-color="var(--color-indigo-900)"
        >
            <img src={logo} alt="Logo dos Jovens da Igreja Adventista do Sétimo dia distrito do Água Verde" slot="icon" />
        </qr-code>
        <!-- <h1 class="text-indigo-900">{presenceUrl}</h1> -->
    {/if}
</div>