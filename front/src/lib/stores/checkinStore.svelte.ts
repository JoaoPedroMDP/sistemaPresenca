const store = $state({
    members: [] as string[],
    addMember(newMember: string) {
        store.members.push(newMember);
    },
})

export default store;