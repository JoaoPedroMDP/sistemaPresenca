import { callLogin, callLogout } from "$lib/api/authApi.svelte";
import type ApiResponse from "$lib/api/index.svelte";
import { LSLoadAuth, LSSaveAuth, LSClearAuth, type Auth } from "$lib/storage/authStorage";

const DAY = 60 * 60 * 24 * 1000; // Dia em milissegundos

interface AuthStoreT {
    loginTrigger: number;
    auth: Auth | null;
    login(username: string, password: string): Promise<{success: boolean, message: string}>;
    logout(): Promise<void>;
    isLogged(): boolean;
    triggerLogin(): void;
}

const store: AuthStoreT = $state<AuthStoreT>({
    loginTrigger: 0,
    auth: null,
    async login(username: string, password: string): Promise<ApiResponse> {
        let response = await callLogin(username, password);

        if(response.success){
            let authData: Auth = {
                loggedAt: new Date().toISOString()
            };
            this.auth = authData;
            LSSaveAuth(authData);
        }

        return response;
    },
    async logout() {
        let response = await callLogout();
        if(response.success){
            LSClearAuth();
            store.auth = null;
        }
    },
    isLogged(): boolean {
        if(!store.auth){
            let loadedAuth = LSLoadAuth();
            if(!loadedAuth){
                return false;
            }
            store.auth = loadedAuth;
        }

        if(store.auth.loggedAt){
            return true;
        }
        return false;
    },
    triggerLogin(): void {
        let now = new Date();
        console.log("Triggering login at " + now.toISOString());
        store.loginTrigger = now.getTime(); // Atualiza o trigger para o timestamp atual
    }
})

export default store;