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
            if(!response.success){
                authStore.goToLogin();
            }

            let member = Member.fromJson(response.data);
            if(member !== undefined && typeof member === "object"){
                store.member = member;
                LSSaveMember(member);
            }else{
                console.log("Resposta da API não contém dados de membro");
                console.log("Resposta completa:", response);
            }
        }

        return store.member;
    }
})

export default store;