<script lang="ts">
    let { 
        value = $bindable(), 
        onkeyup = null,
        label = null,
        cls = '',
        labelCls = '',
        type = 'text',
         } = $props();
</script>

<label>
    {#if label}
        <span class={`label-text text-indigo-900 ${labelCls}`}>{label}</span>
    {/if}
    <input {type} class={`bg-primary text-indigo-900 border-3 rounded-lg border-emerald-500 outline-none p-1 ${cls}`} bind:value={value} {onkeyup} />
</label>