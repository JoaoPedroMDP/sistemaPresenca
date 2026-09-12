export function formatDateInUTC(date: string | null){
    return new Date(date ?? new Date()).toLocaleDateString('pt-BR', {timeZone: 'UTC'})
}
const DAY_MS = 24 * 60 * 60 * 1000;
const BIRTH_WEEK_RADIUS_DAYS = 5;

/**
 *  Lê "AAAA-MM-DD" (isoformat do back) como data local. `new Date("AAAA-MM-DD")`
 *  interpreta como UTC meia-noite e, em fuso negativo, vira o dia anterior.
 */
function parseLocalDate(iso: string): Date | null {
    const [y, m, d] = iso.split('-').map(Number);
    if(!y || !m || !d) return null;
    return new Date(y, m - 1, d);
}

/** Semana do aniversário: é o que dá chapéu e confete ao membro. */
export function isBirthWeek(birthday: string | null, today: Date = new Date()): boolean {
    if(!birthday) return false;

    const birth = parseLocalDate(birthday);
    if(!birth) return false;

    const todayMidnight = new Date(today.getFullYear(), today.getMonth(), today.getDate());

    // Aniversário no ano passado, neste e no próximo: cobre a virada de mês
    // e a de ano (aniversário em 30/12 com hoje em 02/01, por exemplo)
    for(const year of [today.getFullYear() - 1, today.getFullYear(), today.getFullYear() + 1]){
        const anniversary = new Date(year, birth.getMonth(), birth.getDate());
        const diffDays = Math.abs(Math.round((anniversary.getTime() - todayMidnight.getTime()) / DAY_MS));
        if(diffDays <= BIRTH_WEEK_RADIUS_DAYS) return true;
    }

    return false;
}
