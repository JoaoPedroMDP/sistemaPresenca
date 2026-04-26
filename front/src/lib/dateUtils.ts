export function formatDateInUTC(date: string | null){
    return new Date(date ?? new Date()).toLocaleDateString('pt-BR', {timeZone: 'UTC'})
}