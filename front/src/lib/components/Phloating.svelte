<script lang="ts">
    import type { FloatingItem, Photo } from "./types";

    const PHOTO_SIZE = 80;
    const MIN_SPEED = 1;
    const MAX_SPEED = 4;
    const DECELERATION = 0.997;

    let items = $state<FloatingItem[]>([]);
    let containerEl = $state<HTMLDivElement | null>(null);
    let containerWidth = $state(800);
    let containerHeight = $state(600);
    let animFrame: number;

    export function addPhoto({id, name, src}: Photo) {
        console.log("Adding photo to Phloating:", {id, name, src});
        items.push(createItem({id, name, src}));
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
        console.log(s)
        return s;
    }

    function createItem(photo: Photo): FloatingItem {
        return {
            ...photo,
            x: randomBetween(PHOTO_SIZE, containerWidth - PHOTO_SIZE * 2),
            y: randomBetween(PHOTO_SIZE, containerHeight - PHOTO_SIZE * 2),
            vx: randomSpeed() * randomSign(),
            vy: randomSpeed() * randomSign(),
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
            class="floating-photo"
            style="
                transform: translate({item.x}px, {item.y}px);
                width: {PHOTO_SIZE}px;
                height: {PHOTO_SIZE}px;
            "
        >
            {#if !item.src}
                <span class="name">{item.name}</span>
            {:else}
                <img src={item.src} alt={item.name} />
            {/if}
            <!-- <span>{item.vx} {item.vy}</span> -->
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
    }

    .floating-photo img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 50%;
        display: block;
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
</style>