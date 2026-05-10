interface Photo {
    id: string | number;
    src: string;
    name?: string;
}

interface Extras {
    birthday: boolean;
}

interface FloatingItem extends Photo {
    x: number;
    y: number;
    vx: number;
    vy: number;
    extras: Extras;
}


export type { Photo, FloatingItem, Extras };