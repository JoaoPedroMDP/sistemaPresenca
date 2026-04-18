<script lang="ts">
    import Button from "$lib/inputs/Button.svelte";
    import type { Member } from "$lib/types/api";
    import { onMount } from "svelte";
    import type { PageProps } from "./$types";
    import { error } from '@sveltejs/kit';

    let { params }: PageProps = $props()
    let error_str: string|null = $state(null);
    let success: boolean|null = $state(null);
    let pointsEarned = $state<number|null>(10);

    let members: Member[] = $state([]);
    let member: number | null = $state(null)

    onMount(async ()=>{
        const response = await fetch(`/api/presenca/members/pending/${params.code}`);
        let parsed = await response.json();

        if(parsed.error){
            error(parsed.error_code, parsed.error);
        }

        members = parsed.members;
    });

    async function checkin(){
        if(!member){
            error_str = "Selecione um membro para marcar presença";
        }

        let response = await fetch(`/api/presenca/checkin/${params.code}/${member}`, {
            method: "POST"
        });
        let result = await response.json();

        if(result.error){
            error_str = result.error;
        } else {
            setTimeout(() => {
                window.location.href = "https://es.minhaes.org/quizgeral/2/868B043F-A0E7-4ABA-B30A-4F79B2E741D9";
            }, 3000);
            success = true;
            pointsEarned = result.points;
        }
    }

    function teste(){
        success = true;
    }
</script>

<div id="main" data-success={success} class="relative p-4 h-dvh flex flex-col justify-center items-center overflow-hidden">
    <div id="content" data-success={success}>
        <label id="select" class="label flex flex-col text-indigo-900 z-10" data-success={success}>
            <span class="label-text">Quem é?</span>
            <select class="select text-indigo-900 {error_str ? 'border-red-600 border-2': ''}" bind:value={member}>
                {#each members as m}
                    <option class="text-indigo-900" value={m.id}>{m.name}</option>
                {/each}
            </select>
            {#if error_str}
                <span class="label-text text-red-500">{error_str}</span>
            {/if}
        </label>
        <div id="button" data-success={success} class="z-10">
            <Button disabled={!member} onclick={checkin} text="Marcar presença"/>
        </div>
    </div>
    {#if pointsEarned && pointsEarned > 0}
        <span id="points" data-success={success} class="text-black text-2xl">+ {pointsEarned}pts</span>
    {/if}
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

    #points {
        position: absolute;
        bottom: -5%;
        transform: scale(1);
        transition: 
            bottom 1.5s cubic-bezier(.29,.85,.66,.99), 
            transform 1.6s cubic-bezier(.5,.52,.69,.61);
    }
    
    #points[data-success="true"] {
        transform: scale(2);
        bottom: 50%;
        animation: fadeOut 1s ease-in-out 1.5s;
    }
</style>