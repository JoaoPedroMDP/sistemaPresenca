import { loadFromLS, saveToLS, type StoredDataT } from ".";

const KEY = 'device';
const VERSION = 1;

/**
 *  Credencial do aparelho liberado (hoje, o tablet que passa de mão em mão).
 *  O código vem do QR gerado no admin, é resgatado uma única vez e daí em
 *  diante vai no path de toda chamada do dispositivo.
 */
interface Device {
    code: string;
    event: string;
}

interface DeviceT extends StoredDataT {
    data: Device | null;
}

const DEFAULTS: DeviceT = {
    version: VERSION,
    expiresAt: null,
    data: null
}

function LSLoadDevice(): Device | null {
    return loadFromLS(KEY, VERSION, DEFAULTS).data;
}

function LSSaveDevice(device: Device, expiresAt: string | null): void {
    let deviceData: DeviceT = {
        version: VERSION,
        expiresAt: expiresAt,
        data: device
    };
    saveToLS(deviceData, KEY);
}

function LSClearDevice(): void {
    localStorage.removeItem(KEY);
}

export { LSLoadDevice, LSSaveDevice, LSClearDevice };
export type { Device, DeviceT };
