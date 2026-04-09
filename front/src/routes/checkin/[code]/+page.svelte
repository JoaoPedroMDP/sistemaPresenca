<script lang="ts">
    import Button from "$lib/inputs/Button.svelte";
    import type { Member } from "$lib/types/api";
    import type { PageProps } from "./$types";

    let { params, data }: PageProps = $props()
    let error: string|null = $state(null);
    let success: boolean|null = $state(null);

    let members: Member[] = $derived.by(() => {
        return data.members || []
    })
    let member: number | null = $state(null)

    async function checkin(){
        if(!member){
            error = "Selecione um membro para marcar presença";
        }

        let response = await fetch(`/api/ponto/checkin/${params.code}/${member}`, {
            method: "POST"
        });
        let result = await response.json();


        if(result.error){
            error = result.error;
        } else {
            setTimeout(() => {
                window.location.href = "https://es.minhaes.org/quizgeral/2/868B043F-A0E7-4ABA-B30A-4F79B2E741D9";
            }, 1500);
            success = true;
        }
    }

</script>

<div id="main" data-success={success} class="relative p-4 h-dvh flex flex-col justify-center items-center overflow-hidden">
    <div id="content" data-success={success}>
        <label id="select" class="label flex flex-col text-indigo-900 z-10" data-success={success}>
            <span class="label-text">Quem é?</span>
            <select class="select text-indigo-900 {error ? 'border-red-600 border-2': ''}" bind:value={member}>
                {#each members as m}
                    <option class="text-indigo-900" value={m.id}>{m.name}</option>
                {/each}
            </select>
            {#if error}
                <span class="label-text text-red-500">{error}</span>
            {/if}
        </label>
        <div id="button" data-success={success} class="z-10">
            <Button disabled={!member} onclick={checkin} text="Marcar presença"/>
        </div>
    </div>
</div>

<style>
    #main {
        background-color: white;
    }

    #content{
        transform: scale(1);
        transition: transform 0.7s cubic-bezier(.49,-0.43,.65,.83);
    }

    #content[data-success="true"] {
        transform: scale(0);
    }

    #main:before {
        z-index: 0;
        content:'';
        width: 10px;
        height: 10px;
        border-radius: 50%;
        position: absolute;
        background-color: transparent;
        transform: scale(1);
        transition: transform 1.5s ease-in-out;
        overflow: hidden;
    }
    
    #main[data-success="true"]:before {
        content: '';
        background-color: var(--color-emerald-400);
        transform: scale(250);
        overflow: hidden;
    }

    /* #select, #button {
        position: relative;
        transform: scale(1);
        transition: transform 3.5s ease-in-out;
    }

    #select[data-success="true"], #button[data-success="true"] {
        transform: scale(0);
    } */
</style>