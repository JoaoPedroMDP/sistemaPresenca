import authStore from "$lib/stores/authStore.svelte";
import { redirect } from "@sveltejs/kit";

export const load=() => {
    let isLogged = authStore.logged;
    if(!isLogged){
        throw redirect(302, "/login");
    }
}