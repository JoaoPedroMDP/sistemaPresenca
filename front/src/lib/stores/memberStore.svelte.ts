import { LSLoadMember, LSSaveMember } from "$lib/storage/memberStorage";
import type { Member } from "$lib/types/api";

interface MemberStore {
    member: Member | null;
    getMember(): Promise<Member | null>;
}

const store: MemberStore = $state<MemberStore>({
    member: LSLoadMember(),
    async getMember() {
        if(!store.member) {
            console.log("Buscando membro na API");
            let response = await fetch('api/member/me');
            if(!response.ok && response.status == 401){
                console.log(response.statusText);
                return null;
            }
            let memberData = await response.json();
            store.member = memberData;
            LSSaveMember(memberData);
        }

        return store.member;
    }
})

export default store;