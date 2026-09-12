import { goto } from "$app/navigation";
import { callLogged, callLogin, callLogout } from "$lib/api/authApi.svelte";
import type ApiResponse from "$lib/api/index.svelte";
import { LSSaveAuth, LSClearAuth, type Auth } from "$lib/storage/authStorage";

interface AuthStoreT {
    auth: Auth | null;
    login(username: string, password: string): Promise<{success: boolean, message: string}>;
    logout(): Promise<void>;
    getLoggedFromServer(): Promise<boolean>;
    goToLogin(): Promise<void>;
}

const store: AuthStoreT = $state<AuthStoreT>({
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
        await callLogout();
        LSClearAuth();
        store.auth = null;
    },
    async getLoggedFromServer(): Promise<boolean> {
        let response = await callLogged();
        if(!response.success){
            LSClearAuth();
            store.auth = null;
            return false;
        }

        let authData: Auth = {
            loggedAt: new Date().toISOString()
        };
        store.auth = authData;
        LSSaveAuth(authData);
        return true;
    },
    async goToLogin(): Promise<void> {
        await goto('/login');
    }
})

export default store;