interface MemberCheckin {
    name: string;
    photo: string | null;
}

const store = $state({
    members: [] as MemberCheckin[],
    observers: [] as ((member: MemberCheckin) => void)[],
    addMember(name: string, photo: string | null) {
        store.members.push({name, photo});
        for (const observer of store.observers) {
            observer({name, photo});
        }
    },
    registerObserver(observer: (member: MemberCheckin) => void) {
        store.observers.push(observer);
    }
})

export default store;
export type { MemberCheckin };