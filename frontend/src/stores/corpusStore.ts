import { create } from 'zustand';
import type { Corpus } from '../types';

interface CorpusStore {
    corpora: Corpus[];
    activeCorpus: Corpus | null;
    isLoading: boolean;
    error: string | null;

    setCorpora: (corpora: Corpus[]) => void;
    setActiveCorpus: (corpus: Corpus | null) => void;
    addCorpus: (corpus: Corpus) => void;
    removeCorpus: (id: string) => void;
    setLoading: (loading: boolean) => void;
    setError: (error: string | null) => void;
}

export const useCorpusStore = create<CorpusStore>((set) => ({
    corpora: [],
    activeCorpus: null,
    isLoading: false,
    error: null,

    setCorpora: (corpora) => set({ corpora }),

    setActiveCorpus: (corpus) => set({ activeCorpus: corpus }),

    addCorpus: (corpus) =>
        set((state) => ({ corpora: [...state.corpora, corpus] })),

    removeCorpus: (id) =>
        set((state) => ({
            corpora: state.corpora.filter((c) => c.id !== id),
            activeCorpus: state.activeCorpus?.id === id ? null : state.activeCorpus,
        })),

    setLoading: (isLoading) => set({ isLoading }),

    setError: (error) => set({ error }),
}));
