<script lang="ts">
    let { value = $bindable(), label } = $props();
</script>

<label>
    <span class="label-text">{label}</span>
    <input type="text" class="input bg-primary" bind:value={value} />
</label>