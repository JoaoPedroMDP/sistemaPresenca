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
</script>

<div class="member" style="--member-photo-size: {size}px">
    <div class="member-photo-wrap">
        {#if birthday}
            <img src={PartyHat} class="member-hat" alt="Chapéu de aniversário" />
            <div class="confetti-container">
                {#each Array(CONFETTI_COUNT) as _, i}
                    <div
                        class="confetti"
                        style="
                            --delay: {i * 0.15}s;
                            --initial-x: {randomBetween(size / 4, size - size / 4)}px;
                            --target-x: {randomBetween(0, size)}px;
                            --rotation: {randomBetween(0, 360)}deg;
                            background-color: {CONFETTI_COLORS[i % CONFETTI_COLORS.length]};
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
        gap: 4px;
    }

    .member-photo-wrap {
        position: relative;
        line-height: 0;
    }

    .member-photo {
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
        line-height: 1.2;
        max-width: calc(var(--member-photo-size) * 2);
        overflow: hidden;
        text-overflow: ellipsis;
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
