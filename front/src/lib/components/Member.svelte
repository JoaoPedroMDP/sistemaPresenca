<script lang="ts">
    import PartyHat from '$lib/assets/partyhat.png';
    import photoPlaceholder from '$lib/assets/profileAzul.png';

    interface Props {
        name: string;
        /** URL da foto; sem foto cai no placeholder, igual ao PhotoSelector */
        photo?: string | null;
        /** Semana do aniversário: ganha chapéu e confete */
        birthday?: boolean;
        /** Lado da foto em px */
        size?: number;
        showName?: boolean;
    }

    let {
        name,
        photo = null,
        birthday = false,
        size = 80,
        showName = true
    }: Props = $props();

    const CONFETTI_COUNT = 20;
    const CONFETTI_COLORS = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F'];

    function randomBetween(a: number, b: number): number {
        return a + Math.random() * (b - a);
    }

    // Sorteado uma vez por tamanho, não a cada render: senão o confete
    // "pula" de lugar sempre que o componente atualiza
    const confetti = $derived(
        Array.from({ length: CONFETTI_COUNT }, (_, i) => ({
            delay: i * 0.15,
            initialX: randomBetween(size / 4, size - size / 4),
            targetX: randomBetween(0, size),
            rotation: randomBetween(0, 360),
            color: CONFETTI_COLORS[i % CONFETTI_COLORS.length],
        }))
    );
</script>

<div class="member" style="--member-photo-size: {size}px">
    <div class="member-photo-wrap">
        {#if birthday}
            <img src={PartyHat} class="member-hat" alt="Chapéu de aniversário" />
            <div class="confetti-container">
                {#each confetti as piece}
                    <div
                        class="confetti"
                        style="
                            --delay: {piece.delay}s;
                            --initial-x: {piece.initialX}px;
                            --target-x: {piece.targetX}px;
                            --rotation: {piece.rotation}deg;
                            background-color: {piece.color};
                        "
                    ></div>
                {/each}
            </div>
        {/if}
        <img class="member-photo" src={photo || photoPlaceholder} alt={name} />
    </div>
    {#if showName}
        <span class="member-name">{name}</span>
    {/if}
</div>

<style>
    .member {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 6px;
        /* Dentro de grid/flex apertado o item precisa poder encolher o nome
           sem espremer a foto */
        min-width: 0;
        max-width: 100%;
    }

    .member-photo-wrap {
        position: relative;
        line-height: 0;
        flex: 0 0 auto;
    }

    .member-photo {
        display: block;
        width: var(--member-photo-size);
        height: var(--member-photo-size);
        border-radius: 9999px;
        object-fit: cover;
        border: 2px solid var(--color-indigo-900);
        background: white;
    }

    .member-name {
        font-size: 15px;
        font-weight: 600;
        color: var(--color-indigo-950);
        text-align: center;
        line-height: 1.25;
        /* Nunca passa da largura do card; nome comprido quebra em até duas
           linhas e só então recebe reticências */
        max-width: 100%;
        display: -webkit-box;
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 2;
        line-clamp: 2;
        overflow: hidden;
        overflow-wrap: anywhere;
    }

    .member-hat {
        position: absolute;
        right: -1rem;
        top: -1rem;
        width: 2.5rem;
        height: 2.5rem;
        transform: rotate(30deg);
        object-fit: contain;
        pointer-events: none;
        z-index: 1;
    }

    .confetti-container {
        position: absolute;
        top: 100%;
        pointer-events: none;
        width: 100%;
        height: 100%;
    }

    .confetti {
        position: absolute;
        width: 8px;
        height: 8px;
        top: 0;
        left: var(--initial-x);
        opacity: 0;
        animation: confetti-fall 2s infinite;
        animation-delay: var(--delay);
    }

    @keyframes confetti-fall {
        0% {
            transform: translate(-50%, 0px) rotate(0deg);
            opacity: 1;
        }
        100% {
            transform: translate(calc(-50% + var(--target-x)), 200px) rotate(var(--rotation));
            opacity: 0;
        }
    }
</style>
