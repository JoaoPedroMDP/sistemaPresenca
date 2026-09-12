<script lang="ts">
    import type { Extras, FloatingItem, Photo } from "./types";
    import Member from "./Member.svelte";

    const PHOTO_SIZE = 80;
    const MIN_SPEED = 2;
    const MAX_SPEED = 5;
    const DECELERATION = 0.997;

    let items = $state<FloatingItem[]>([]);
    let containerEl = $state<HTMLDivElement | null>(null);
    let containerWidth = $state(800);
    let containerHeight = $state(600);
    let animFrame: number;

    let {debug = false} = $props();

    let itemElements = new Map<string | number, HTMLElement>();

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
            // Medido no primeiro tick: com o nome embaixo da foto o item é
            // mais largo que PHOTO_SIZE, e a colisão com a borda usa isso
            width: undefined,
            height: undefined,
            extras: extras,
        };
    }

    function ensureItemSize(item: FloatingItem): FloatingItem {
        if (item.width && item.height) {
            return item;
        }
        
        const el = itemElements.get(item.id);
        if (el) {
            item.width = el.offsetWidth;
            item.height = el.offsetHeight;
        }
        
        return item;
    }

    function tick() {
        items = items.map((item: FloatingItem) => {
            item = ensureItemSize(item);
            
            let { x, y, vx, vy, width = PHOTO_SIZE, height = PHOTO_SIZE } = item;

            x += vx;
            y += vy;

            vx = applyDeceleration(vx);
            vy = applyDeceleration(vy);

            if (x <= 0) {
                x = 0;
                vx = MAX_SPEED;
            } else if (x + width >= containerWidth) {
                x = containerWidth - width;
                vx = -MAX_SPEED;
            }

            if (y <= 0) {
                y = 0;
                vy = MAX_SPEED;
            } else if (y + height >= containerHeight) {
                y = containerHeight - height;
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

    function trackPhoto(node: HTMLElement, id: string | number) {
        itemElements.set(id, node);

        return {
            destroy() {
                itemElements.delete(id);
            }
        };
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
        use:trackPhoto={item.id}
        style="transform: translate({item.x}px, {item.y}px);" 
        class="absolute will-change-transform"
        >
        <Member
            name={item.name ?? ''}
            photo={item.src}
            birthday={item.extras.birthday}
            size={PHOTO_SIZE}
        />
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

</style>