interface User{
    id: number;
    username: string;
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
                username: json.user.username
            } : null,
            json.photo
        );
    }
};

export type { MemberI, User };
export { Member };