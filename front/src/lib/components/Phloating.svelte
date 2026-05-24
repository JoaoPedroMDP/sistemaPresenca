<script lang="ts">
    import type { Extras, FloatingItem, Photo } from "./types";
    import PartyHat from '$lib/assets/partyhat.png';

    const PHOTO_SIZE = 80;
    const MIN_SPEED = 1;
    const MAX_SPEED = 2;
    const DECELERATION = 0.997;
    const CONFETTI_COUNT = 20;
    const CONFETTI_COLORS = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F'];

    let items = $state<FloatingItem[]>([]);
    let containerEl = $state<HTMLDivElement | null>(null);
    let containerWidth = $state(800);
    let containerHeight = $state(600);
    let animFrame: number;

    let {debug = false} = $props();


    export function addPhoto({id, name, src}: Photo, extras: Extras) {
        console.log("Adding photo to Phloating:", {id, name, src});
        items.push(createItem({id, name, src}, extras));
    }

    function applyDeceleration(speed: number): number {
        let newSpeed = speed * DECELERATION;
        if (Math.abs(newSpeed) < MIN_SPEED){
            return speed;
        }

        return newSpeed;
    }

    function randomBetween(a: number, b: number): number {
        return a + Math.random() * (b - a);
    }

    function randomSign(): 1 | -1 {
        return Math.random() > 0.5 ? 1 : -1;
    }

    function randomSpeed(): number{
        let s = randomBetween(MIN_SPEED, MAX_SPEED); 
        return s;
    }

    function createItem(photo: Photo, extras: Extras): FloatingItem {
        return {
            ...photo,
            x: randomBetween(PHOTO_SIZE, containerWidth - PHOTO_SIZE * 2),
            y: randomBetween(PHOTO_SIZE, containerHeight - PHOTO_SIZE * 2),
            vx: randomSpeed() * randomSign(),
            vy: randomSpeed() * randomSign(),
            extras: extras,
        };
    }

    function tick() {
        items = items.map((item: FloatingItem) => {
            let { x, y, vx, vy } = item;

            x += vx;
            y += vy;

            vx = applyDeceleration(vx);
            vy = applyDeceleration(vy);

            if (x <= 0) {
                x = 0;
                vx = MAX_SPEED;
            } else if (x + PHOTO_SIZE >= containerWidth) {
                x = containerWidth - PHOTO_SIZE;
                vx = -MAX_SPEED;
            }

            if (y <= 0) {
                y = 0;
                vy = MAX_SPEED;
            } else if (y + PHOTO_SIZE >= containerHeight) {
                y = containerHeight - PHOTO_SIZE;
                vy = -MAX_SPEED;
            }

            return { ...item, x, y, vx, vy };
        });

        animFrame = requestAnimationFrame(tick);
    }

    function updateSize() {
        if (!containerEl) return;
        containerWidth = containerEl.clientWidth;
        containerHeight = containerEl.clientHeight;
    }

    $effect(() => {
        updateSize();
        window.addEventListener("resize", updateSize);
        animFrame = requestAnimationFrame(tick);

        return () => {
            cancelAnimationFrame(animFrame);
            window.removeEventListener("resize", updateSize);
        };
    });
</script>

<div class="floating-container" bind:this={containerEl}>
    {#each items as item (item.id)}
        <div 
        style="width: {PHOTO_SIZE}px; height: {PHOTO_SIZE}px; transform: translate({item.x}px, {item.y}px);" 
        class="absolute"
        >
        {#if item.extras.birthday}
            <img src={PartyHat} class="absolute rotate-30 -right-4 -top-4 w-10 h-10 object-contain pointer-events-none z-1" alt="Birthday Hat" />
            <div class="confetti-container">
                {#each Array(CONFETTI_COUNT) as _, i}
                    <div 
                        class="confetti" 
                        style="
                            --delay: {i * 0.15}s;
                            --initial-x: {randomBetween(0 + PHOTO_SIZE/4, PHOTO_SIZE - PHOTO_SIZE/4)}px;
                            --target-x: {randomBetween(0, PHOTO_SIZE)}px;
                            --rotation: {randomBetween(0, 360)}deg;
                            background-color: {CONFETTI_COLORS[i % CONFETTI_COLORS.length]};
                        "
                    ></div>
                {/each}
            </div>
        {/if}
        {#if !item.src}
            <span class="name">{item.name}</span>
        {:else}
            <img src={item.src} alt={item.name} class="floating-photo" 
                style="width: {PHOTO_SIZE}px; height: {PHOTO_SIZE}px;"/>
        {/if}
        {#if debug }
            <div class="absolute top-0 left-0 flex flex-col">
                <span class="bg-white text-black">X: {item.x.toFixed(0)}</span>
                <span class="bg-white text-black">Y: {item.y.toFixed(0)}</span>
            </div>
        {/if}
        </div>
    {/each}
</div>

<style>
    .floating-container {
        position: absolute;
        inset: 0;
        overflow: hidden;
        pointer-events: none;
    }

    .floating-photo {
        position: absolute;
        top: 0;
        left: 0;
        will-change: transform;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;
        overflow: visible;
    }

    .name {
        font-size: 15px;
        font-weight: 600;
        color: var(--color-indigo-950);
        background: transparent;
        padding: 2px 6px;
        max-width: 180px;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .confetti-container {
        position: absolute;
        top: 100%;
        /* left: 50%; */
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