const store = $state({
    code: undefined as string | undefined,
    setCode(newCode: string) {
        store.code = newCode;
    },
    useCode() {
        const code = store.code;
        store.code = '';
        return code;
    }
})

export default store;