import api from './api';
import type { Corpus, CreateCorpusDTO, ApiResponse } from '../types';

export const corpusService = {
    // List all corpora
    async list(): Promise<Corpus[]> {
        const response = await api.get<{ corpora: Corpus[] }>('/v1/corpus');
        return response.data.corpora || [];
    },

    // Get single corpus
    async get(id: string): Promise<Corpus> {
        const response = await api.get<Corpus>(`/v1/corpus/${id}`);
        return response.data;
    },

    // Create corpus from text
    async createFromText(data: CreateCorpusDTO): Promise<Corpus> {
        const formData = new FormData();
        formData.append('name', data.name);
        if (data.corpus_text) {
            formData.append('corpus_text', data.corpus_text);
        }
        if (data.split_mode) {
            formData.append('split_mode', data.split_mode);
        }

        const response = await api.post<Corpus>('/v1/corpus', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
    },

    // Create corpus from file
    async createFromFile(name: string, file: File, splitMode?: string): Promise<Corpus> {
        const formData = new FormData();
        formData.append('name', name);
        formData.append('file', file);
        if (splitMode) {
            formData.append('split_mode', splitMode);
        }

        const response = await api.post<Corpus>('/corpus/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
    },

    // Activate corpus
    async activate(id: string): Promise<void> {
        await api.post(`/v1/corpus/${id}/activate`);
    },

    // Delete corpus
    async delete(id: string): Promise<void> {
        await api.delete(`/v1/corpus/${id}`);
    },
};
