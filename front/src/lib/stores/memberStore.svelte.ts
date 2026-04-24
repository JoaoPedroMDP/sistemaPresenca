import { callMe } from "$lib/api/memberApi.svelte";
import { LSLoadMember, LSSaveMember } from "$lib/storage/memberStorage";
import { Member, type memberI } from "$lib/types/api";

interface MemberStore {
    member: memberI | null;
    getMember(): Promise<memberI | null>;
}

const store: MemberStore = $state<MemberStore>({
    member: LSLoadMember(),
    async getMember() {
        if(!store.member) {
            console.log("Buscando membro na API");
            let response = await callMe();
            if(!response.success){
                console.log(response.message);
                return null;
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