export function formatDateInUTC(date: string | null){
    return new Date(date ?? new Date()).toLocaleDateString('pt-BR', {timeZone: 'UTC'})
}
/** Semana do aniversário: é o que dá chapéu e confete ao membro. */
export function isBirthWeek(birthday: string | null): boolean {
    if(!birthday) return false;

    const today = new Date();
    const birthDate = new Date(birthday);

    return birthDate.getMonth() === today.getMonth()
        && Math.abs(birthDate.getDate() - today.getDate()) <= 5;
}
