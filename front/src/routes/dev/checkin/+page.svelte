<script lang="ts">
    import { onMount } from 'svelte';
    import Button from '$lib/inputs/Button.svelte';
    import Member from '$lib/components/Member.svelte';
    import { isBirthWeek } from '$lib/dateUtils';
    import {
        callDevEvents,
        callDevMembers,
        callDevCheckin,
        callDevReset,
        type DevMember,
    } from '$lib/api/devApi.svelte';

    const PHOTO_SIZE = 72;

    let eventName = $state('Escola Sabatina');
    let events = $state<string[]>([]);
    let members = $state<DevMember[]>([]);
    let selected = $state(new Set<number>());
    let search = $state('');
    let intervalMs = $state(500);
    let amount = $state(10);
    let loading = $state(false);
    let running = $state(false);
    let message = $state('');
    let log = $state<string[]>([]);

    let filtered = $derived(
        members.filter((m) => m.name.toLowerCase().includes(search.trim().toLowerCase()))
    );
    let doneToday = $derived(members.filter((m) => m.checked_in_today).length);
    // Só quem ainda não marcou hoje: repetir alguém não mexeria no painel
    let pending = $derived(members.filter((m) => !m.checked_in_today));

    function addLog(line: string) {
        const now = new Date().toLocaleTimeString('pt-BR');
        log = [`${now} — ${line}`, ...log].slice(0, 50);
    }

    async function loadEvents() {
        const response = await callDevEvents();
        if (response.success && response.data) {
            events = response.data.events;
            if (events.length > 0 && !events.includes(eventName)) {
                eventName = events[0];
            }
        }
    }

    async function loadMembers() {
        loading = true;
        message = '';
        const response = await callDevMembers(eventName);
        loading = false;

        if (!response.success || !response.data) {
            members = [];
            message = response.message;
            return;
        }

        members = response.data.members;
        // A seleção é por id e sobrevive ao recarregar: quem sumiu da lista sai
        const ids = new Set(members.map((m) => m.id));
        selected = new Set([...selected].filter((id) => ids.has(id)));
    }

    function toggle(id: number) {
        const next = new Set(selected);
        if (next.has(id)) {
            next.delete(id);
        } else {
            next.add(id);
        }
        selected = next;
    }

    function selectAll() {
        selected = new Set(filtered.map((m) => m.id));
    }

    function clearSelection() {
        selected = new Set();
    }

    async function sleep(ms: number) {
        return new Promise((resolve) => setTimeout(resolve, ms));
    }

    async function checkin(ids: number[]) {
        if (running || ids.length === 0) return;

        running = true;
        message = '';

        // Um id por chamada, com intervalo: o painel enche aos poucos, como
        // aconteceria numa fila de verdade
        for (const [i, id] of ids.entries()) {
            const response = await callDevCheckin(eventName, [id]);

            if (!response.success || !response.data) {
                addLog(`erro: ${response.message}`);
                message = response.message;
                break;
            }

            for (const result of response.data.results) {
                if (result.error) {
                    addLog(`membro ${result.id}: ${result.error}`);
                } else if (result.already) {
                    addLog(`${result.name} — já tinha check-in hoje, painel não avisado`);
                } else {
                    addLog(`${result.name} — check-in feito, ${result.points} pts`);
                }
            }

            if (i < ids.length - 1 && intervalMs > 0) {
                await sleep(intervalMs);
            }
        }

        running = false;
        await loadMembers();
    }

    async function checkinSelected() {
        // Ordem da lista, não a de clique: previsível ao conferir o painel
        await checkin(members.filter((m) => selected.has(m.id)).map((m) => m.id));
        clearSelection();
    }

    /** Sorteia N dos pendentes, sem repetir (Fisher-Yates parcial). */
    function sample(pool: DevMember[], n: number): DevMember[] {
        const copy = [...pool];
        const take = Math.min(n, copy.length);
        for (let i = 0; i < take; i++) {
            const j = i + Math.floor(Math.random() * (copy.length - i));
            [copy[i], copy[j]] = [copy[j], copy[i]];
        }
        return copy.slice(0, take);
    }

    async function checkinAmount() {
        const wanted = Math.floor(amount);
        if (wanted < 1) {
            message = 'Informe uma quantidade maior que zero.';
            return;
        }

        // Sorteados em vez dos N primeiros: assim o painel varia entre rodadas
        // e aniversariante ou foto vazia aparecem sem eu caçar na lista
        const picked = sample(pending, wanted);
        if (picked.length === 0) {
            message = 'Todo mundo já marcou presença hoje. Use o reset.';
            return;
        }

        if (picked.length < wanted) {
            addLog(`só havia ${picked.length} pendentes dos ${wanted} pedidos`);
        }

        await checkin(picked.map((m) => m.id));
    }

    async function reset() {
        const ok = confirm(
            'Apagar TODOS os check-ins, scores e quadros de pontuação?\n\n' +
            'Os quadros são recriados com: uv run python manage.py populate_db'
        );
        if (!ok) return;

        running = true;
        const response = await callDevReset();
        running = false;

        if (!response.success || !response.data) {
            message = response.message;
            return;
        }

        const { checkins, scores, scoreboards } = response.data.deleted;
        addLog(`reset: ${checkins} check-ins, ${scores} scores, ${scoreboards} quadros apagados`);
        clearSelection();
        await loadMembers();
    }

    // onMount, não $effect: loadMembers lê eventName, e num efeito isso
    // recarregaria a lista a cada tecla digitada no campo de evento
    onMount(() => {
        loadEvents();
        loadMembers();
    });
</script>

<div class="flex flex-col h-full bg-white text-indigo-950">
    <header class="flex items-center justify-between gap-4 px-6 py-4 bg-indigo-900 text-white">
        <div class="flex flex-col gap-0.5">
            <strong class="text-xl font-semibold">Simulador de check-in</strong>
            <span class="text-xs opacity-75">Só existe em desenvolvimento</span>
        </div>
        <Button onclick={reset} disabled={running} text="Resetar tudo" cls="bg-red-600" />
    </header>

    <div class="flex flex-wrap items-center gap-3 px-6 pt-4">
        <label class="flex items-center gap-2">
            <span class="text-sm text-gray-600">Evento</span>
            <input
                class="text-lg p-2 text-indigo-900 border-3 rounded-lg border-emerald-500 outline-none"
                list="dev-events"
                autocomplete="off"
                bind:value={eventName}
            />
            <datalist id="dev-events">
                {#each events as name}
                    <option value={name}></option>
                {/each}
            </datalist>
        </label>
        <Button onclick={loadMembers} disabled={running} text="Carregar" />

        <label class="flex items-center gap-2">
            <span class="text-sm text-gray-600">Quantidade</span>
            <input
                type="number"
                min="1"
                step="1"
                class="w-24 text-lg p-2 text-indigo-900 border-3 rounded-lg border-emerald-500 outline-none"
                bind:value={amount}
            />
        </label>
        <Button
            onclick={checkinAmount}
            disabled={running || pending.length === 0}
            text={running ? 'Simulando…' : `Simular ${amount} aleatórios`}
            cls="bg-emerald-600"
        />

        <label class="flex items-center gap-2">
            <span class="text-sm text-gray-600">Intervalo</span>
            <input
                type="number"
                min="0"
                step="100"
                class="w-24 text-lg p-2 text-indigo-900 border-3 rounded-lg border-emerald-500 outline-none"
                bind:value={intervalMs}
            />
            <span class="text-sm text-gray-600">ms</span>
        </label>
    </div>

    <div class="flex flex-wrap items-center gap-3 px-6 pt-3">
        <input
            class="flex-1 min-w-[200px] text-lg p-2 text-indigo-900 border-3 rounded-lg border-emerald-500 outline-none"
            placeholder="Buscar nome…"
            autocomplete="off"
            bind:value={search}
        />
        <Button onclick={selectAll} disabled={running} text="Selecionar todos" cls="bg-gray-600" />
        <Button onclick={clearSelection} disabled={running} text="Limpar" cls="bg-gray-600" />
        <Button
            onclick={checkinSelected}
            disabled={running || selected.size === 0}
            text={running ? 'Simulando…' : `Simular ${selected.size} selecionados`}
            cls="bg-emerald-600"
        />
        <span class="px-3 py-1 rounded-full bg-gray-100 text-gray-700 text-sm">
            {doneToday}/{members.length} presentes hoje · {pending.length} pendentes
        </span>
    </div>

    {#if message}
        <p class="px-6 pt-3 text-red-600 text-sm">{message}</p>
    {/if}

    <div class="grid gap-4 px-6 pt-5 pb-4 flex-1 min-h-0 overflow-y-auto content-start member-grid">
        {#each filtered as m (m.id)}
            <div
                class="relative flex flex-col items-center gap-2 min-w-0 pt-7 px-2 pb-3 border-2 rounded-2xl
                       {selected.has(m.id) ? 'border-emerald-500 bg-emerald-50' : 'border-gray-200 bg-white'}
                       {m.checked_in_today ? 'opacity-50' : ''}"
            >
                <button
                    class="flex items-center justify-center min-w-0 cursor-pointer"
                    onclick={() => toggle(m.id)}
                >
                    <Member
                        name={m.name}
                        photo={m.photo}
                        birthday={isBirthWeek(m.birthday)}
                        size={PHOTO_SIZE}
                    />
                </button>

                <button
                    class="px-3 py-1 rounded-full bg-indigo-900 text-white text-xs cursor-pointer
                           disabled:opacity-40 disabled:cursor-default"
                    disabled={running}
                    onclick={() => checkin([m.id])}
                >
                    Check-in agora
                </button>

                {#if m.checked_in_today}
                    <span class="absolute top-2 left-2 px-2 py-0.5 rounded-full bg-emerald-500 text-white text-[10px]">
                        já marcou
                    </span>
                {/if}
            </div>
        {/each}
    </div>

    {#if !loading && filtered.length === 0}
        <p class="py-10 text-center text-gray-500">Nenhum membro encontrado.</p>
    {/if}

    <footer class="shrink-0 max-h-40 overflow-y-auto px-6 py-3 bg-gray-50 border-t border-gray-200
                   text-xs text-gray-600 font-mono">
        {#if log.length === 0}
            <span>O resultado de cada simulação aparece aqui.</span>
        {:else}
            {#each log as line}
                <div>{line}</div>
            {/each}
        {/if}
    </footer>
</div>

<style>
    .member-grid {
        grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    }
</style>
