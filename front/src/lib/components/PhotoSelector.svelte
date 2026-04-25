<script lang="ts">
    import { callSetPhoto } from "$lib/api/memberApi.svelte";
    import photoPlaceholder from "$lib/assets/profileAzul.png";

    interface Props {
        src?: string | null;
        alt?: string;
        onerror?: (msg: string) => void;
    }

    let { src = $bindable(null), alt = 'Foto de perfil', onerror }: Props = $props();

    let fileInput: HTMLInputElement;
    let cropModal = $state(false);
    let canvas: HTMLCanvasElement;
    let cropCanvas: HTMLCanvasElement;
    let img = new Image();

    // Crop state em coordenadas da imagem natural
    let cropX = 0;
    let cropY = 0;
    let cropSize = 0;
    let uploading = $state(false);

    // Drag (1 dedo / mouse)
    let dragging = false;
    let dragStartX = 0;
    let dragStartY = 0;
    let dragOriginX = 0;
    let dragOriginY = 0;

    // Pinch (2 dedos)
    let pinching = false;
    let pinchStartDist = 0;
    let pinchStartSize = 0;
    let pinchStartCX = 0;
    let pinchStartCY = 0;

    // rAF throttle
    let rafPending = false;

    // ── Init ──────────────────────────────────────────────────────────────────

    function openFilePicker() { fileInput.click(); }

    function onFileSelected(e: Event) {
        const file = (e.target as HTMLInputElement).files?.[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (ev) => {
            img = new Image();
            img.onload = () => {
                // Tamanho inicial: 60% do menor lado da imagem, centralizado
                const minSide = Math.min(img.naturalWidth, img.naturalHeight);
                cropSize = Math.round(minSide * 0.6);
                cropX = Math.round((img.naturalWidth  - cropSize) / 2);
                cropY = Math.round((img.naturalHeight - cropSize) / 2);
                cropModal = true;
                requestDraw();
            };
            img.src = ev.target?.result as string;
        };
        reader.readAsDataURL(file);
        (e.target as HTMLInputElement).value = '';
    }

    // ── Draw ──────────────────────────────────────────────────────────────────

    function requestDraw() {
        if (rafPending) return;
        rafPending = true;
        requestAnimationFrame(() => {
            rafPending = false;
            drawCropPreview();
        });
    }

    function drawCropPreview() {
        if (!canvas || !img.complete) return;
        // Só redimensiona o canvas quando necessário (evita reset desnecessário)
        if (canvas.width !== img.naturalWidth || canvas.height !== img.naturalHeight) {
            canvas.width  = img.naturalWidth;
            canvas.height = img.naturalHeight;
        }
        const ctx = canvas.getContext('2d')!;
        const cx = cropX + cropSize / 2;
        const cy = cropY + cropSize / 2;
        const r  = cropSize / 2;

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);

        // Overlay escuro com buraco circular
        ctx.save();
        ctx.fillStyle = 'rgba(0,0,0,0.55)';
        ctx.beginPath();
        ctx.rect(0, 0, canvas.width, canvas.height);
        ctx.arc(cx, cy, r, 0, Math.PI * 2, true); // true = sentido horário inverso = buraco
        ctx.fill('evenodd');
        ctx.restore();

        // Imagem dentro do círculo (nítida, sem overlay)
        ctx.save();
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.clip();
        ctx.drawImage(img, 0, 0);
        ctx.restore();

        // Borda
        ctx.strokeStyle = '#6366f1';
        ctx.lineWidth = Math.max(3, img.naturalWidth / 300); // escala com a imagem
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.stroke();
    }

    $effect(() => {
        if (cropModal && canvas && img.complete) requestDraw();
    });

    // ── Coordenadas canvas ────────────────────────────────────────────────────

    function toImgCoords(clientX: number, clientY: number) {
        const rect = canvas.getBoundingClientRect();
        return {
            x: (clientX - rect.left)  * (img.naturalWidth  / rect.width),
            y: (clientY - rect.top)   * (img.naturalHeight / rect.height),
        };
    }

    function clampCrop() {
        cropX = Math.max(0, Math.min(img.naturalWidth  - cropSize, cropX));
        cropY = Math.max(0, Math.min(img.naturalHeight - cropSize, cropY));
    }

    // ── Mouse ─────────────────────────────────────────────────────────────────

    function onMouseDown(e: MouseEvent) {
        const { x, y } = toImgCoords(e.clientX, e.clientY);
        const cx = cropX + cropSize / 2;
        const cy = cropY + cropSize / 2;
        if (Math.hypot(x - cx, y - cy) <= cropSize / 2) {
            dragging = true;
            dragStartX = x; dragStartY = y;
            dragOriginX = cropX; dragOriginY = cropY;
        }
    }

    function onMouseMove(e: MouseEvent) {
        if (!dragging) return;
        const { x, y } = toImgCoords(e.clientX, e.clientY);
        cropX = dragOriginX + (x - dragStartX);
        cropY = dragOriginY + (y - dragStartY);
        clampCrop();
        requestDraw();
    }

    function onMouseUp() { dragging = false; }

    function onWheel(e: WheelEvent) {
        e.preventDefault();
        const cx = cropX + cropSize / 2;
        const cy = cropY + cropSize / 2;
        const delta = e.deltaY > 0 ? -0.05 : 0.05;
        const minSide = Math.min(img.naturalWidth, img.naturalHeight);
        cropSize = Math.max(minSide * 0.1, Math.min(minSide, cropSize * (1 + delta)));
        cropX = cx - cropSize / 2;
        cropY = cy - cropSize / 2;
        clampCrop();
        requestDraw();
    }

    // ── Touch ─────────────────────────────────────────────────────────────────

    function touchDist(t: TouchList) {
        return Math.hypot(
            t[0].clientX - t[1].clientX,
            t[0].clientY - t[1].clientY,
        );
    }

    function touchMid(t: TouchList) {
        return {
            x: (t[0].clientX + t[1].clientX) / 2,
            y: (t[0].clientY + t[1].clientY) / 2,
        };
    }

    function onTouchStart(e: TouchEvent) {
        e.preventDefault();
        if (e.touches.length === 1) {
            // 1 dedo → drag
            pinching = false;
            const { x, y } = toImgCoords(e.touches[0].clientX, e.touches[0].clientY);
            const cx = cropX + cropSize / 2;
            const cy = cropY + cropSize / 2;
            // Permite arrastar de qualquer lugar (mais confortável em mobile)
            dragging = true;
            dragStartX = x; dragStartY = y;
            dragOriginX = cropX; dragOriginY = cropY;
        } else if (e.touches.length === 2) {
            // 2 dedos → pinch
            dragging = false;
            pinching = true;
            pinchStartDist = touchDist(e.touches);
            pinchStartSize = cropSize;
            const mid = touchMid(e.touches);
            const imgMid = toImgCoords(mid.x, mid.y);
            pinchStartCX = imgMid.x;
            pinchStartCY = imgMid.y;
        }
    }

    function onTouchMove(e: TouchEvent) {
        e.preventDefault();
        if (dragging && e.touches.length === 1) {
            const { x, y } = toImgCoords(e.touches[0].clientX, e.touches[0].clientY);
            cropX = dragOriginX + (x - dragStartX);
            cropY = dragOriginY + (y - dragStartY);
            clampCrop();
            requestDraw();
        } else if (pinching && e.touches.length === 2) {
            const ratio = touchDist(e.touches) / pinchStartDist;
            const minSide = Math.min(img.naturalWidth, img.naturalHeight);
            cropSize = Math.max(minSide * 0.1, Math.min(minSide, pinchStartSize * ratio));
            // Mantém o centro do pinch estável
            cropX = pinchStartCX - cropSize / 2;
            cropY = pinchStartCY - cropSize / 2;
            clampCrop();
            requestDraw();
        }
    }

    function onTouchEnd(e: TouchEvent) {
        if (e.touches.length === 0) { dragging = false; pinching = false; }
        else if (e.touches.length === 1 && pinching) {
            // Voltou para 1 dedo após pinch: reinicia drag a partir da posição atual
            pinching = false;
            const { x, y } = toImgCoords(e.touches[0].clientX, e.touches[0].clientY);
            dragging = true;
            dragStartX = x; dragStartY = y;
            dragOriginX = cropX; dragOriginY = cropY;
        }
    }

    // ── Confirm ───────────────────────────────────────────────────────────────

    async function confirmCrop() {
        if (!cropCanvas) return;
        cropCanvas.width = 400;
        cropCanvas.height = 400;
        const ctx = cropCanvas.getContext('2d')!;
        ctx.beginPath();
        ctx.arc(200, 200, 200, 0, Math.PI * 2);
        ctx.clip();
        ctx.drawImage(img, cropX, cropY, cropSize, cropSize, 0, 0, 400, 400);

        const blob = await new Promise<Blob | null>((res) => cropCanvas.toBlob(res, 'image/jpeg', 0.92));
        if (!blob) return;

        uploading = true;
        try {
            const result = await callSetPhoto(blob);
            if (result.success) {
                src = URL.createObjectURL(blob);
                cropModal = false;
            } else {
                onerror?.(result.message ?? 'Erro ao enviar foto.');
            }
        } finally {
            uploading = false;
        }
    }

    function cancelCrop() { cropModal = false; }
</script>

<!-- Hidden inputs -->
<input bind:this={fileInput} type="file" accept="image/*" class="hidden" onchange={onFileSelected} />
<canvas bind:this={cropCanvas} class="hidden"></canvas>

<!-- Crop modal -->
{#if cropModal}
    <div class="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/70 px-4 gap-4">
        <span class="text-white text-sm opacity-70">
            Arraste para reposicionar · Pinça para redimensionar
        </span>

        <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
        <canvas
            bind:this={canvas}
            class="rounded-xl cursor-grab active:cursor-grabbing touch-none select-none"
            style="max-width: min(90vw, 500px); max-height: 65dvh; width: auto; height: auto;"
            onmousedown={onMouseDown}
            onmousemove={onMouseMove}
            onmouseup={onMouseUp}
            onmouseleave={onMouseUp}
            ontouchstart={onTouchStart}
            ontouchmove={onTouchMove}
            ontouchend={onTouchEnd}
            onwheel={onWheel}
            role="img"
            aria-label="Editor de recorte de foto"
        ></canvas>

        <div class="flex gap-3">
            <button
                class="px-6 py-2 rounded-full bg-gray-600 text-white font-medium"
                onclick={cancelCrop}
                disabled={uploading}
            >
                Cancelar
            </button>
            <button
                class="px-6 py-2 rounded-full bg-indigo-900 text-white font-medium flex items-center gap-2 disabled:opacity-60"
                onclick={confirmCrop}
                disabled={uploading}
            >
                {#if uploading}
                    <span class="icon-[svg-spinners--ring-resize] text-lg"></span>
                    Enviando…
                {:else}
                    Confirmar
                {/if}
            </button>
        </div>
    </div>
{/if}

<!-- Avatar button -->
<button
    class="relative group rounded-full aspect-square focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-900"
    onclick={openFilePicker}
    aria-label="Alterar foto de perfil"
    title="Alterar foto de perfil"
>
    <img
        width="100" height="100"
        src={src || photoPlaceholder}
        {alt}
        class="border-2 border-indigo-900 rounded-full object-cover w-[100px] h-[100px] transition-opacity group-hover:opacity-70"
    />
    <span class="
        absolute inset-0 flex items-center justify-center
        rounded-full bg-black/30 opacity-0 group-hover:opacity-100
        transition-opacity pointer-events-none
    ">
        <span class="icon-[fa6-solid--camera] text-white text-2xl"></span>
    </span>
</button>