interface Photo {
    id: string | number;
    src: string | null;
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
    width?: number;
    height?: number;
}


export type { Photo, FloatingItem, Extras };