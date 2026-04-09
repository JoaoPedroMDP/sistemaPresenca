<script lang="ts">
    let { 
        onclick,
        disabled = false,
        text = undefined, 
        icon = undefined,
        cls = undefined
    } = $props();
</script>

<button class="btn bg-indigo-900 disabled:bg-transparent disabled:border-2 border-indigo-900 m-2 disabled:text-indigo-900 {cls}" {onclick} disabled={disabled}>
    {#if text}
        <span>{text}</span>
    {/if}
    {#if icon}
        <span class="icon-[{icon}]"></span>
    {/if}
</button>