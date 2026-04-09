<script lang="ts">
	import { page } from '$app/state';
</script>

<div class="flex flex-col justify-center items-center h-dvh text-center p-4 bg-red-600">
    <h1 class="text-4xl text-white border-b-2 border-black w-[75%]">{page.status}</h1>
    <h3 class="text-2xl mt-4">{page.error.message}</h3>
</div>