<script lang="ts">
    interface Props {
        onclick?: (e: MouseEvent) => void;
        disabled?: boolean;
        text?: string;
        cls?: string;
    }

    let {
        onclick,
        disabled = false,
        text = undefined,
        cls = ''
    }: Props = $props();
</script>

<button class="
    p-2 rounded-md bg-indigo-900 disabled:bg-transparent 
    disabled:border-2 border-indigo-900 m-2 
    disabled:text-indigo-900 text-white 
    {cls}" {onclick} disabled={disabled}>
    {#if text}
        <span>{text}</span>
    {/if}
</button>
