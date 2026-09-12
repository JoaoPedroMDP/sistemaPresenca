<script lang="ts">
    interface Props {
        value?: string | null;
        onkeyup?: (e: KeyboardEvent) => void;
        label?: string | null;
        cls?: string;
        labelCls?: string;
        type?: string;
    }

    let {
        value = $bindable(),
        onkeyup = undefined,
        label = null,
        cls = '',
        labelCls = '',
        type = 'text',
    }: Props = $props();
</script>

<label>
    {#if label}
        <span class={`label-text text-indigo-900 ${labelCls}`}>{label}</span>
    {/if}
    <input {type} class={`bg-primary text-indigo-900 border-3 rounded-lg border-emerald-500 outline-none p-1 ${cls}`} bind:value={value} {onkeyup} />
</label>
