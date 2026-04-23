import { LSLoadAuth, LSSaveAuth, LSClearAuth, type Auth } from "$lib/storage/authStorage";

const DAY = 60 * 60 * 24 * 1000; // Dia em milissegundos

interface AuthStoreT {
    auth: Auth | null;
    login(username: string, password: string): Promise<{success: boolean, message: string}>;
    logout(): Promise<void>;
}

const store: AuthStoreT = $state<AuthStoreT>({
    auth: null,
    async login(username: string, password: string): Promise<{success: boolean, message: string}> {
        let response = await fetch("/api/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username,
                password
            })
        });

        if(!response.ok){
            console.log("Erro na resposta do login:", response.status, response.statusText);
            return {
                "success": false,
                "message": response.statusText
            };
        }
        let data = await response.json();
        if(data.error){
            console.log("Erro no login:", data.error);
            return {
                "success": false,
                "message": data.error
            };
        }

        let authData: Auth = {
            loggedAt: new Date().toISOString()
        };
        this.auth = authData;
        LSSaveAuth(authData);

        return {"success": true, "message": "Login successful"};
    },
    async logout() {
        let response = await fetch("/api/auth/logout");
        if(response.ok){
            LSClearAuth();
            store.auth = null;
        }
    }
})

export default store;