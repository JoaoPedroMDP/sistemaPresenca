<script lang="ts">
    import type { PhloatingHandlers } from '$lib/components/Phloating.svelte';
    import user from '$lib/assets/profileAzul.png';
    import azul from '$lib/assets/jovensLogoAzul.png';
    import branca from '$lib/assets/jovensLogoBranca.png';
    import { onMount } from 'svelte';
    import Phloating from '$lib/components/Phloating.svelte';

    let phloating: PhloatingHandlers | null = $state(null); 

    onMount(() => {
        if(phloating){
            phloating.addPhoto({
                id: '1',
                name: 'João',
                src: user
            }, { birthday: '2026-05-15' });
            phloating.addPhoto({
                id: '2',
                name: 'Pedro',
                src: azul
            }, { birthday: '2026-03-15' });
            phloating.addPhoto({
                id: '3',
                name: 'Martins',
                src: branca
            }, { birthday: '2026-05-15' });
            phloating.addPhoto({
                id: '4',
                name: 'João',
                src: user
            }, { birthday: '2026-05-15' });
            phloating.addPhoto({
                id: '5',
                name: 'Pedro',
                src: azul
            }, { birthday: '2026-03-15' });
            phloating.addPhoto({
                id: '6',
                name: 'Martins',
                src: branca
            }, { birthday: '2026-05-15' });
        }
    });
</script>

<Phloating bind:this={phloating} debug={true}/>
