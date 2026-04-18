<script lang="ts">
    import { goto } from "$app/navigation";
    
    import authStore from "$lib/stores/authStore.svelte";
    import Text from "$lib/inputs/Text.svelte";
    import logo from "$lib/assets/jovensLogoAzul.png";
    import Button from "$lib/inputs/Button.svelte";
    let username: string | null = $state(null);
    let password: string | null = $state(null);
    let message = $state('');

    async function login(): Promise<void> {
        console.log("Entrar com", username, password);
        if(!username || !password){
            message = 'Preencha todos os campos';
            return;
        }
        let results = await authStore.login(username, password);
        if(!results.success){
            message = results.message;
            return;
        }
        goto('/me');
    }

    function oku_login(e: KeyboardEvent): void {
        if(e.key === 'Enter'){
            login();
        }
    }
</script>

<div class="h-dvh flex flex-col items-center justify-center gap-4">
    <span class="text-2xl text-indigo-900">{message}</span>
    <img src={logo} alt="Logo">
    <Text label="Usuário" bind:value={username}/>
    <Text label="Senha" bind:value={password} type="password" onkeyup={oku_login}/>
    <Button text="Entrar" onclick={login}/>
</div>