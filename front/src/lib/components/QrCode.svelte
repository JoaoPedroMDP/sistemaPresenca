<script lang="ts">
    import { qr } from '@svelte-put/qr/svg';
    import codeStore from '$lib/stores/codeStore.svelte';
    import logo from '$lib/assets/jovensLogoVerde.png';

    const presenceUrl = $derived(
        codeStore.code
            ? `${window.location.protocol}//${window.location.host}/checkin/${codeStore.code}`
            : null
    )

    // Tempo de vida restante do código no momento em que ele chega;
    // o anel nasce cheio e drena até expiresAt
    const remainingMs = $derived(
        codeStore.expiresAt
            ? Math.max(new Date(codeStore.expiresAt).getTime() - Date.now(), 0)
            : 0
    )

    // Quadrado arredondado começando no topo-centro, sentido horário
    function ringPath(inset: number, radius: number): string {
        const a = inset;
        const b = 100 - inset;
        const r = radius;
        return [
            `M 50 ${a}`,
            `H ${b - r}`, `A ${r} ${r} 0 0 1 ${b} ${a + r}`,
            `V ${b - r}`, `A ${r} ${r} 0 0 1 ${b - r} ${b}`,
            `H ${a + r}`, `A ${r} ${r} 0 0 1 ${a} ${b - r}`,
            `V ${a + r}`, `A ${r} ${r} 0 0 1 ${a + r} ${a}`,
            `H 50`,
        ].join(' ');
    }
</script>

<div class="flex flex-col items-center overflow-hidden">
    {#if !presenceUrl}
        <p>Aguardando código...</p>
    {:else}
        <div class="relative p-3">
            {#key codeStore.code}
                <svg
                    class="absolute inset-0 h-full w-full"
                    viewBox="0 0 100 100"
                    preserveAspectRatio="none"
                    aria-hidden="true"
                >
                    <path
                        class="countdown-ring"
                        d={ringPath(1.25, 5.25)}
                        pathLength="100"
                        style="animation-duration: {remainingMs}ms"
                    />
                </svg>
            {/key}
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
        </div>
        {#if import.meta.env.MODE == 'development'}
            <a href={presenceUrl} target="_blank" class="text-blue-300">{presenceUrl}</a>
        {/if}
    {/if}
</div>

<style>
    .countdown-ring {
        fill: none;
        /* Mesmo azul dos módulos do QR (moduleFill) */
        stroke: #312e81;
        stroke-width: 2.5;
        /* Cap reto: cap redondo sobressai da ponta e deixa um resíduo
           no topo quando o anel esvazia por completo */
        stroke-linecap: butt;
        /* pathLength="100" normaliza o perímetro: dasharray/dashoffset em %.
           Gap enorme: sem ele o padrão repete a cada 200 unidades e erros de
           arredondamento do navegador deixam uma lasca do traço no offset 100 */
        stroke-dasharray: 100 900;
        stroke-dashoffset: 0;
        animation: drain linear forwards;
    }

    @keyframes drain {
        98% {
            opacity: 1;
        }
        to {
            stroke-dashoffset: 100;
            /* Esconde qualquer resíduo de arredondamento no fim */
            opacity: 0;
        }
    }
</style>
