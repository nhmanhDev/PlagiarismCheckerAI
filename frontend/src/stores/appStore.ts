import { create } from 'zustand';
import type { SystemStatus } from '../types';

interface AppStore {
    systemStatus: SystemStatus | null;
    setSystemStatus: (status: SystemStatus) => void;
}

export const useAppStore = create<AppStore>((set) => ({
    systemStatus: null,
    setSystemStatus: (systemStatus) => set({ systemStatus }),
}));
