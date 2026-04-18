interface User{
    id: number;
    username: string;
}

interface Member{
    id: number;
    name: string;
    birthday: string|null;
    user: User|null;
}

export type { Member, User };