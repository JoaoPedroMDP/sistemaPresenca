<script lang="ts">
    let { 
        value = $bindable(), 
        onkeyup,
        label = null,
        cls = '',
        labelCls = '',
         } = $props();
</script>

<label>
    {#if label}
        <span class={`label-text ${labelCls}`}>{label}</span>
    {/if}
    <input type="text" class={`input bg-primary ${cls}`} bind:value={value} {onkeyup} />
</label>