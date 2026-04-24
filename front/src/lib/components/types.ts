interface Photo {
    id: string | number;
    src: string;
    name?: string;
}

interface FloatingItem extends Photo {
    x: number;
    y: number;
    vx: number;
    vy: number;
}

export type { Photo, FloatingItem }