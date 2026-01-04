import api from './api';
import type { CheckParams, CheckResponse, SystemStatus } from '../types';

export const plagiarismService = {
    // Basic hybrid check
    async check(params: CheckParams): Promise<CheckResponse> {
        const formData = new FormData();
        formData.append('query_text', params.query_text);
        if (params.alpha !== undefined) formData.append('alpha', params.alpha.toString());
        if (params.top_k_lex) formData.append('top_k_lex', params.top_k_lex.toString());
        if (params.top_k_sem) formData.append('top_k_sem', params.top_k_sem.toString());
        if (params.top_n) formData.append('top_n', params.top_n.toString());
        if (params.threshold) formData.append('threshold', params.threshold.toString());

        const response = await api.post<CheckResponse>('/v1/plagiarism/check', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
    },

    // Multi-stage check with re-ranker
    async checkMultistage(params: CheckParams): Promise<CheckResponse> {
        const formData = new FormData();
        formData.append('query_text', params.query_text);
        if (params.alpha !== undefined) formData.append('alpha', params.alpha.toString());
        if (params.top_n) formData.append('top_n', params.top_n.toString());
        if (params.threshold) formData.append('threshold', params.threshold.toString());
        formData.append('use_reranker', params.use_reranker ? 'true' : 'false');

        const response = await api.post<CheckResponse>('/v1/plagiarism/check-multistage', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
    },

    // Multi-stage check with file upload
    async checkMultistageWithFile(
        file: File,
        alpha: number = 0.4,
        useReranker: boolean = true
    ): Promise<CheckResponse> {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('alpha', alpha.toString());
        formData.append('top_n', '5');
        formData.append('threshold', '0.75');
        formData.append('use_reranker', useReranker ? 'true' : 'false');

        const response = await api.post<CheckResponse>('/v1/plagiarism/check-multistage', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
    },

    // Get system status
    async getStatus(): Promise<SystemStatus> {
        const response = await api.get<SystemStatus>('/v1/system/status');
        return response.data;
    },
};
