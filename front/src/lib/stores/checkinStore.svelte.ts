interface MemberCheckin {
    name: string;
    photo: string | null;
    birthday: string | null;
}

const store = $state({
    members: [] as MemberCheckin[],
    observers: [] as ((member: MemberCheckin) => void)[],
    addMember(name: string, photo: string | null, birthday: string | null) {
        store.members.push({name, photo, birthday});
        for (const observer of store.observers) {
            observer({name, photo, birthday});
        }
    },
    registerObserver(observer: (member: MemberCheckin) => void) {
        store.observers.push(observer);
    }
})

export default store;
export type { MemberCheckin };