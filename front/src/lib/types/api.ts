// Espelha MeUserResponse do back (presenca/api/member.py)
interface User{
    id: number;
    email: string;
}

interface MemberI{
    id: number;
    name: string;
    birthday: string|null;
    user: User|null;
    photo: string|null;
}

interface Member extends MemberI {};

class Member{
    constructor(id: number, name: string, birthday: string|null, user: User|null, photo: string|null){
        this.id = id;
        this.name = name;
        this.birthday = birthday;
        this.user = user;
        this.photo = photo;
    }

    static fromJson(json: any): Member {
        return new Member(
            json.id,
            json.name,
            json.birthday,
            json.user ? {
                id: json.user.id,
                email: json.user.email
            } : null,
            json.photo
        );
    }
};

export type { MemberI, User };
export { Member };
// Linha do placar (presenca/api/score.py, get_scoreboard_for_event)
interface ScoreEntry {
    name: string;
    score: number;
}

// Item de /api/checkin/pending/<code>: só id e nome, sem foto
interface PendingMember {
    id: number;
    name: string;
}

export type { ScoreEntry, PendingMember };
