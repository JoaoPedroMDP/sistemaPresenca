const store = $state({
    code: undefined as string | undefined,
    expiresAt: undefined as string | undefined,
    setCode(newCode: string, expiresAt: string) {
        store.code = newCode;
        store.expiresAt = expiresAt;
    }
})

export default store;
