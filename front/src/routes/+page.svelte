<script lang="ts">
	import { initSocket } from '$lib/websocket/socket';
	import QrCode from "$lib/components/QrCode.svelte";
	import codeStore from "$lib/stores/codeStore.svelte";
	import "$lib/websocket/socket";
    import Text from '$lib/inputs/Text.svelte';
    import Phloating from '$lib/components/Phloating.svelte';
    import type { PhloatingHandlers } from '$lib/components/Phloating.svelte';
	import checkinStore, { type MemberCheckin } from '$lib/stores/checkinStore.svelte';
    import { callAlreadyCheckedIn } from '$lib/api/checkinApi.svelte';
    import Button from '$lib/inputs/Button.svelte';

	let connected: boolean = $state(false);
	let event_name: string = $state('Escola Sabatina');

	let phloating: PhloatingHandlers | null = $state(null); 

	async function loadPreviousCheckins(group_name: string){
		let response = await callAlreadyCheckedIn(group_name);
		if(response.success && response.data){
			response.data.members.forEach(member => {
				memberCheckin(member);
			});
		}
		else{
			console.error("Failed to fetch already checked-in members:", response.error);
		}
	}

	async function enterGroup(group_name: string) : Promise<void> {
		connected = await initSocket(group_name);
		if(connected){
			await loadPreviousCheckins(group_name);
		}
	}

	async function onkeyup(e: KeyboardEvent): Promise<void> {
		if(e.key === 'Enter'){
			await enterGroup(event_name);
		}
	}

	function isBirthWeek(birthday: string | null): boolean {
		if(!birthday) return false;

		const today = new Date();
		const birthDate = new Date(birthday);
		const birthMonth = birthDate.getMonth();
		const birthDay = birthDate.getDate();

		const todayMonth = today.getMonth();
		const todayDay = today.getDate();

		return birthMonth === todayMonth && Math.abs(birthDay - todayDay) <= 3;
	}

	function memberCheckin(member: MemberCheckin) {
		if(!phloating){
			console.log("Phloating component not initialized yet");
			return;
		}

		let extras = {
			birthday: isBirthWeek(member.birthday)
		};

		phloating.addPhoto(
			{id: member.name, name: member.name, src: member.photo},
			extras
		);
	}

	checkinStore.registerObserver(memberCheckin);
</script>

<div class="flex flex-row items-center justify-center h-dvh gap-8 text-black">
	{#if !connected}
		<div class="flex flex-col items-center gap-4">
			<p class="text-2xl text-indigo-900">Digite o nome do evento para gerar o QR Code</p>
			<Text bind:value={event_name} {onkeyup}/>
			<Button onclick={() => enterGroup(event_name)} text="Entrar"></Button>
		</div>
	{:else}
		{#if codeStore.code}
		<div class="flex flex-col items-center gap-4">
			<h1 class="text-4xl text-indigo-900 z-10">Registre sua presença!!</h1>
			<div class="relative flex justify-center items-center w-min z-10">
				<QrCode />
			</div>
			<Phloating bind:this={phloating}/>
		</div>
		{/if}
	{/if}
</div>