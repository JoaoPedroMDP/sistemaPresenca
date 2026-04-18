import { browser } from "$app/environment";

function getFromLocalStorage(key: string) {
    if(!browser) {
        return null;
    }

    let value = localStorage.getItem(key);

    if(value) {
        return JSON.parse(value);
    }
    return null;
}

function saveToLocalStorage(key: string, value: any) {
    if(!browser) {
        return;
    }
    localStorage.setItem(key, JSON.stringify(value));
}

const store = $state({
    logged: getFromLocalStorage("logged") || false,
    member: getFromLocalStorage("member"),
    setLogged(logged: boolean) {
        store.logged = logged;
        saveToLocalStorage("logged", store.logged);
    },
    setMember(member: any) {
        store.member = member;
        saveToLocalStorage("member", store.member);
    },
    async getMember() {
        if(!store.logged) {
            return null;
        }

        if(!store.member) {
            let fromStorage = getFromLocalStorage("member");
            if(fromStorage) {
                store.member = fromStorage;
            }else{
                let response = await fetch('api/member/me');
                if(!response.ok && response.status == 401){
                    console.log(response.statusText);
                    return null;
                }
                store.member = await response.json();
            }


            saveToLocalStorage("member", store.member);
        }

        return store.member;
    },
    async login(username: string, password: string) {
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
            console.log(response);
            console.log(response.ok);
            console.log(response.statusText);
            return {
                "success": false,
                "message": response.statusText
            };
        }
        let data = await response.json();
        if(data.error){
            return {
                "success": false,
                "message": data.error
            };
        }

        store.setLogged(true);
        return {"success": true}
    },
    async logout() {
        let response = await fetch("/api/auth/logout");
        if(response.ok){
            store.setLogged(false);
            store.setMember(null);
            saveToLocalStorage("logged", false);
            saveToLocalStorage("member", null);
        }
    }
})

export default store;