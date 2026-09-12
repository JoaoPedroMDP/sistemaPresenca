import { callMe } from "$lib/api/memberApi.svelte";
import { LSLoadMember, LSSaveMember } from "$lib/storage/memberStorage";
import { Member, type MemberI } from "$lib/types/api";
import authStore from "./authStore.svelte";


interface MemberStore {
    member: MemberI | null;
    getMember(): Promise<MemberI | null>;
}

const store: MemberStore = $state<MemberStore>({
    member: LSLoadMember(),
    async getMember() {
        if(!store.member) {
            console.log("Buscando membro na API");
            let response = await callMe();
            if(!response.success || !response.data){
                console.log("Não foi possível buscar o membro:", response.message);
                await authStore.goToLogin();
                return null;
            }

            let member = Member.fromJson(response.data);
            store.member = member;
            LSSaveMember(member);
        }

        return store.member;
    }
})

export default store;