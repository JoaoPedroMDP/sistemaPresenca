<script lang="ts">
    import type { Extras, FloatingItem, Photo } from "./types";
    import Member from "./Member.svelte";

    const PHOTO_SIZE = 80;
    const MIN_SPEED = 2;
    const MAX_SPEED = 5;
    // Fator de desaceleração por frame de 60fps; com dt variável vira
    // DECELERATION ^ (dt / FRAME_MS)
    const DECELERATION = 0.997;
    const FRAME_MS = 1000 / 60;
    // Passo máximo por frame: se a TV engasga, o item não teleporta
    const MAX_STEP = 3;
    // O movimento é lento o bastante para 30fps não aparecer, e metade dos
    // frames é metade do trabalho de composição na TV
    const TARGET_FPS = 60;
    // Tolerância de meio frame de 60Hz: sem ela um frame que chega 0,1ms cedo
    // é descartado e a taxa real despenca para 20fps
    const MIN_DELTA = 1000 / TARGET_FPS - FRAME_MS / 2;

    // $state.raw: a lista só é reativa quando um item entra ou sai. A posição
    // de cada item é mutada fora do sistema de reatividade e escrita direto no
    // DOM pelo loop, sem re-render do Svelte a cada frame
    let items = $state.raw<FloatingItem[]>([]);
    let containerEl: HTMLDivElement | null = null;
    let containerWidth = 800;
    let containerHeight = 600;
    let animFrame: number;
    let lastTime = 0;

    let itemElements = new Map<string | number, HTMLElement>();

    export function addPhoto({id, name, src}: Photo, extras: Extras) {
        items = [...items, createItem({id, name, src}, extras)];
    }

    function applyDeceleration(speed: number, factor: number): number {
        let newSpeed = speed * factor;
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
            // Medido quando o elemento monta: com o nome embaixo da foto o item
            // é mais largo que PHOTO_SIZE, e a colisão com a borda usa isso
            width: undefined,
            height: undefined,
            extras: extras,
        };
    }

    function tick(time: number) {
        animFrame = requestAnimationFrame(tick);

        const elapsed = time - lastTime;
        // lastTime não avança aqui: o tempo do frame pulado entra no próximo
        if (elapsed < MIN_DELTA) return;

        // Movimento em px/frame de 60fps, normalizado pelo tempo real: a
        // animação corre na mesma velocidade em 30 ou em 60fps
        const step = Math.min(elapsed / FRAME_MS, MAX_STEP);
        lastTime = time;
        if (step <= 0) return;

        const decel = DECELERATION ** step;

        for (const item of items) {
            const width = item.width ?? PHOTO_SIZE;
            const height = item.height ?? PHOTO_SIZE;

            item.x += item.vx * step;
            item.y += item.vy * step;

            item.vx = applyDeceleration(item.vx, decel);
            item.vy = applyDeceleration(item.vy, decel);

            if (item.x <= 0) {
                item.x = 0;
                item.vx = MAX_SPEED;
            } else if (item.x + width >= containerWidth) {
                item.x = containerWidth - width;
                item.vx = -MAX_SPEED;
            }

            if (item.y <= 0) {
                item.y = 0;
                item.vy = MAX_SPEED;
            } else if (item.y + height >= containerHeight) {
                item.y = containerHeight - height;
                item.vy = -MAX_SPEED;
            }

            const el = itemElements.get(item.id);
            if (el) {
                // translate3d mantém o item na sua própria camada, sem repintar
                el.style.transform = `translate3d(${item.x}px, ${item.y}px, 0)`;
            }
        }
    }

    function updateSize() {
        if (!containerEl) return;
        containerWidth = containerEl.clientWidth;
        containerHeight = containerEl.clientHeight;
    }

    function trackPhoto(node: HTMLElement, item: FloatingItem) {
        itemElements.set(item.id, node);
        // Uma medida só, na montagem: ler offsetWidth dentro do loop forçaria
        // layout a cada frame
        item.width = node.offsetWidth;
        item.height = node.offsetHeight;
        node.style.transform = `translate3d(${item.x}px, ${item.y}px, 0)`;

        return {
            destroy() {
                itemElements.delete(item.id);
            }
        };
    }

    function trackContainer(node: HTMLDivElement) {
        containerEl = node;
        updateSize();

        const observer = new ResizeObserver(updateSize);
        observer.observe(node);

        lastTime = performance.now();
        animFrame = requestAnimationFrame(tick);

        return () => {
            cancelAnimationFrame(animFrame);
            observer.disconnect();
            containerEl = null;
        };
    }
</script>

<div class="floating-container" {@attach trackContainer}>
    {#each items as item (item.id)}
        <div use:trackPhoto={item} class="floating-item">
            <Member
                name={item.name ?? ''}
                photo={item.src}
                birthday={item.extras.birthday}
                size={PHOTO_SIZE}
            />
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

    .floating-item {
        position: absolute;
        top: 0;
        left: 0;
        will-change: transform;
        /* O chapéu de aniversário passa da borda do item, então nada de
           contain: paint aqui */
        contain: layout;
    }
</style>
