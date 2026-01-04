// API Response Types
export interface ApiResponse<T> {
    data?: T;
    error?: string;
    message?: string;
}

// Corpus Types
export interface Corpus {
    id: string;
    name: string;
    created_at: string;
    segment_count: number;
    is_active?: boolean;
}

export interface CreateCorpusDTO {
    name: string;
    corpus_text?: string;
    file?: File;
    split_mode?: 'auto' | 'sentence' | 'paragraph';
}

// Plagiarism Check Types
export interface CheckParams {
    query_text: string;
    alpha?: number;
    top_k_lex?: number;
    top_k_sem?: number;
    top_n?: number;
    threshold?: number;
    use_reranker?: boolean;
}

export interface PlagiarismResult {
    index: number;
    text: string;
    score_final: number;
    score_lexical_raw?: number;
    score_semantic_raw?: number;
    rerank_score?: number;
    hybrid_rerank_score?: number;
    is_suspected: boolean;
}

export interface CheckResponse {
    query: string;
    results: PlagiarismResult[];
    alpha: number;
    threshold: number;
    corpus_id: string;
    vietnamese_detected: boolean;
    method?: string;
    reranker_used?: boolean;
    device: string;
    timestamp: string;
}

// Statistics
export interface SystemStatus {
    status: 'ok' | 'error';
    device: string;
    vietnamese_available: boolean;
    pdf_available: boolean;
    reranker_available?: boolean;
}
